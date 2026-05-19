"""Lowercase MicroStrategy user names through mstrio-py.

Edit CONFIG below or provide MSTR_LIBRARY_URL, MSTR_USERNAME and
MSTR_PASSWORD environment variables before running.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from getpass import getpass
from typing import Iterable

import pandas as pd
from mstrio.connection import Connection
from mstrio.users_and_groups.user import User, list_users


CONFIG = {
    "library_url": os.getenv("MSTR_LIBRARY_URL", "https://YOUR_LIBRARY_URL/MicroStrategyLibrary"),
    "username": os.getenv("MSTR_USERNAME", "YOUR_ADMIN_USERNAME"),
    "password": os.getenv("MSTR_PASSWORD", "YOUR_ADMIN_PASSWORD"),
    "login_mode": int(os.getenv("MSTR_LOGIN_MODE", "1")),
}


SYSTEM_USER_NAMES = {
    "administrator",
    "guest",
    "public / guest",
    "public/guest",
    "system administrator",
    "mstr user",
    "microstrategy administrator",
}

UPPERCASE_RE = re.compile(r"[A-Z]")


@dataclass(frozen=True)
class UserChange:
    id: str
    display_name: str
    login_id: str
    trust_id: str
    new_display_name: str
    new_login_id: str
    new_trust_id: str


def has_uppercase(value: object) -> bool:
    return isinstance(value, str) and bool(UPPERCASE_RE.search(value))


def lowercase_or_none(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return str(value).lower()


def is_placeholder(value: str) -> bool:
    return value.startswith("YOUR_") or "YOUR_LIBRARY_URL" in value


def prompt_yes_no(message: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{message} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes", "是", "确认", "剔除"}


def connect() -> Connection:
    library_url = CONFIG["library_url"]
    username = CONFIG["username"]
    password = CONFIG["password"]

    if is_placeholder(library_url):
        library_url = input("请输入 MSTR Library URL: ").strip()
    if is_placeholder(username):
        username = input("请输入登录用户名: ").strip()
    if is_placeholder(password):
        password = getpass("请输入登录密码: ")

    print(f"\n正在登录 Library: {library_url}")
    return Connection(
        base_url=library_url,
        username=username,
        password=password,
        login_mode=CONFIG["login_mode"],
    )


def users_to_dataframe(users: list[User]) -> pd.DataFrame:
    rows = []
    for user in users:
        rows.append(
            {
                "id": getattr(user, "id", None),
                "display_name": getattr(user, "name", None) or getattr(user, "full_name", None),
                "full_name": getattr(user, "full_name", None),
                "login_id": getattr(user, "username", None) or getattr(user, "abbreviation", None),
                "account_login": getattr(user, "abbreviation", None),
                "trust_id": getattr(user, "trust_id", None),
                "enabled": getattr(user, "enabled", None),
            }
        )
    return pd.DataFrame(rows)


def print_user_list(df: pd.DataFrame, title: str) -> None:
    print(f"\n{title}，数量: {len(df)}")
    if df.empty:
        return
    preferred_columns = [
        "display_name",
        "login_id",
        "account_login",
        "trust_id",
        "new_display_name",
        "new_login_id",
        "new_trust_id",
        "success",
        "message",
        "enabled",
    ]
    columns = [column for column in preferred_columns if column in df.columns]
    if not columns:
        columns = list(df.columns)
    print(df[columns].fillna("").to_string(index=False))


def find_uppercase_users(df: pd.DataFrame) -> pd.DataFrame:
    text_columns = ["display_name", "full_name", "login_id", "account_login", "trust_id"]
    selected = df[text_columns]
    if hasattr(selected, "map"):
        uppercase_cells = selected.map(has_uppercase)
    else:
        uppercase_cells = selected.applymap(has_uppercase)
    mask = uppercase_cells.any(axis=1)
    return df[mask].copy()


def filter_system_users(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    def is_system(row: pd.Series) -> bool:
        values = {
            str(row.get("display_name") or "").strip().lower(),
            str(row.get("full_name") or "").strip().lower(),
            str(row.get("login_id") or "").strip().lower(),
            str(row.get("account_login") or "").strip().lower(),
        }
        return bool(values & SYSTEM_USER_NAMES)

    system_mask = df.apply(is_system, axis=1)
    return df[~system_mask].copy(), df[system_mask].copy()


def build_changes(df: pd.DataFrame) -> list[UserChange]:
    changes = []
    for row in df.itertuples(index=False):
        display_name = row.display_name or row.full_name or row.login_id
        login_id = row.login_id or row.account_login
        trust_id = row.trust_id
        changes.append(
            UserChange(
                id=row.id,
                display_name=display_name or "",
                login_id=login_id or "",
                trust_id=trust_id or "",
                new_display_name=lowercase_or_none(display_name) or "",
                new_login_id=lowercase_or_none(login_id) or "",
                new_trust_id=lowercase_or_none(trust_id) or "",
            )
        )
    return changes


def validate_no_login_collisions(all_users_df: pd.DataFrame, changes: Iterable[UserChange]) -> None:
    changes = list(changes)
    changed_ids = {change.id for change in changes}
    existing_logins = {
        str(row.login_id).lower(): row.id
        for row in all_users_df.itertuples(index=False)
        if row.id not in changed_ids and pd.notna(row.login_id) and row.login_id
    }

    seen_in_batch: dict[str, str] = {}
    errors = []
    for change in changes:
        login = change.new_login_id
        if not login:
            errors.append(f"{change.display_name}: 登录 ID 为空，无法更新")
            continue
        if login in existing_logins:
            errors.append(f"{change.login_id} -> {login}: 与现有用户 ID {existing_logins[login]} 冲突")
        if login in seen_in_batch:
            errors.append(f"{change.login_id} -> {login}: 与本批次用户 ID {seen_in_batch[login]} 冲突")
        seen_in_batch[login] = change.id

    if errors:
        print("\n发现小写化后的登录 ID 冲突，已停止执行：")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(2)


def apply_changes(connection: Connection, changes: list[UserChange], dry_run: bool = False) -> pd.DataFrame:
    results = []
    for change in changes:
        print(f"\n处理用户: {change.display_name} / {change.login_id} -> {change.new_login_id}")
        try:
            if not dry_run:
                user = User(connection=connection, id=change.id)
                user.alter(
                    username=change.new_login_id,
                    full_name=change.new_display_name,
                    trust_id=change.new_trust_id or None,
                    journal_comment="Batch lowercase user display name, login ID and trusted auth ID.",
                )
            results.append(
                {
                    "display_name": change.display_name,
                    "login_id": change.login_id,
                    "new_display_name": change.new_display_name,
                    "new_login_id": change.new_login_id,
                    "new_trust_id": change.new_trust_id,
                    "success": True,
                    "message": "dry-run" if dry_run else "updated",
                }
            )
            print("结果: 成功" if not dry_run else "结果: 预演成功")
        except Exception as exc:
            results.append(
                {
                    "display_name": change.display_name,
                    "login_id": change.login_id,
                    "new_display_name": change.new_display_name,
                    "new_login_id": change.new_login_id,
                    "new_trust_id": change.new_trust_id,
                    "success": False,
                    "message": str(exc),
                }
            )
            print(f"结果: 失败 - {exc}")
    return pd.DataFrame(results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch lowercase MSTR user fields through mstrio-py.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating MSTR.")
    parser.add_argument("--yes", action="store_true", help="Skip final confirmation before update.")
    args = parser.parse_args()

    connection = connect()

    print("\n正在列出当前平台全部用户名...")
    users = list_users(connection=connection)
    users_df = users_to_dataframe(users)
    print_user_list(users_df, "当前平台全部用户")

    print("\n已将用户清单导入 DataFrame。")
    uppercase_df = find_uppercase_users(users_df)
    print_user_list(uppercase_df, "包含大写字母的用户")

    if uppercase_df.empty:
        print("\n未发现需要小写化的用户。检查完成。")
        return 0

    candidate_df, system_df = filter_system_users(uppercase_df)
    if not system_df.empty:
        print_user_list(system_df, "疑似 MSTR 平台自带用户")
        if prompt_yes_no("是否剔除这些疑似平台自带用户？默认剔除", default=True):
            uppercase_df = candidate_df
            print("\n已剔除疑似平台自带用户。")
        else:
            print("\n保留疑似平台自带用户。")

    changes = build_changes(uppercase_df)
    validate_no_login_collisions(users_df, changes)

    preview_df = pd.DataFrame([change.__dict__ for change in changes])
    print_user_list(preview_df, "确认待小写化用户列表")
    print(f"\n待处理大写用户数量: {len(changes)}")

    if not changes:
        print("\n剔除后没有需要处理的用户。检查完成。")
        return 0

    if not args.dry_run and not args.yes:
        if not prompt_yes_no("是否确认将以上用户全部进行小写化？", default=False):
            print("\n用户取消操作，未修改任何用户。")
            return 1

    result_df = apply_changes(connection, changes, dry_run=args.dry_run)
    print_user_list(result_df, "运行结果")

    if not result_df["success"].all():
        print("\n存在失败项，请根据上方错误信息处理后重试。")
        return 2

    print("\n再次列出当前平台用户名...")
    refreshed_users = list_users(connection=connection)
    refreshed_df = users_to_dataframe(refreshed_users)
    print_user_list(refreshed_df, "当前平台全部用户")

    remaining_targets = find_uppercase_users(refreshed_df)
    processed_ids = {change.id for change in changes}
    remaining_processed = remaining_targets[remaining_targets["id"].isin(processed_ids)]

    if args.dry_run:
        print("\nDry-run 模式未实际修改用户。预演检查完成。")
        return 0

    if remaining_processed.empty:
        print("\n检查成功：本批次目标用户已完成小写化。")
        print("恭喜，批处理脚本运行成功！")
        return 0

    print_user_list(remaining_processed, "仍包含大写字母的本批次用户")
    print("\n检查失败：部分本批次目标用户仍包含大写字母。")
    return 2


if __name__ == "__main__":
    sys.exit(main())
