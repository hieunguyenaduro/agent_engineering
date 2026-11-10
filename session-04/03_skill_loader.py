"""03 — Skill loader: chỉ nạp mô tả trước, nạp thân bài khi thật sự cần.

Chạy: python 03_skill_loader.py
Đọc hai file trong skills/. Không gọi model, không cần API key.
"""

from pathlib import Path

from common.tokens import estimate_tokens, print_table, shorten

SKILL_DIR = Path(__file__).with_name("skills")


class Skill:
    """Một skill đã quét metadata. Thân bài chưa nằm trong bộ nhớ."""

    def __init__(self, path: Path, meta: dict):
        self.path = path
        self.name = meta.get("name", path.parent.name)
        self.description = meta.get("description", "")
        self.when_to_use = meta.get("when_to_use", "")
        self.meta_text = f"{self.name}: {self.description} Dùng khi: {self.when_to_use}"

    @property
    def keywords(self) -> list:
        return [k.strip().lower() for k in self.when_to_use.split(",") if k.strip()]

    def score(self, query: str) -> int:
        q = query.lower()
        return sum(1 for k in self.keywords if k in q)


def read_metadata(path: Path) -> dict:
    """Đọc từng dòng, dừng ở '---' thứ hai: không kéo thân bài vào bộ nhớ."""
    meta = {}
    with path.open(encoding="utf-8") as f:
        if f.readline().strip() != "---":
            raise ValueError(f"{path} thiếu frontmatter")
        for line in f:
            if line.strip() == "---":
                break
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    for field in ("name", "description", "when_to_use"):
        if not meta.get(field):
            raise ValueError(f"{path} thiếu trường {field}")
    return meta


class Registry:
    def __init__(self, root: Path):
        self.skills = []
        for path in sorted(root.glob("*/SKILL.md")):
            self.skills.append(Skill(path, read_metadata(path)))

    def match(self, query: str):
        scored = [(s.score(query), s) for s in self.skills]
        scored = [(score, s) for score, s in scored if score > 0]
        return max(scored, key=lambda pair: pair[0])[1] if scored else None

    def load_body(self, skill: Skill) -> str:
        """Chỉ lúc này mới đọc toàn văn. Đây là progressive disclosure."""
        text = skill.path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        return parts[2].strip() if len(parts) == 3 else text

    def metadata_tokens(self) -> int:
        return sum(estimate_tokens(s.meta_text) for s in self.skills)

    def body_tokens(self, skill: Skill) -> int:
        return estimate_tokens(self.load_body(skill))


def main():
    registry = Registry(SKILL_DIR)
    print(f"[scan] Tìm thấy {len(registry.skills)} skill. Chỉ đọc frontmatter.\n")

    rows = []
    for skill in registry.skills:
        # Đọc thân bài ở đây chỉ để đo chi phí so sánh. Loader thật không làm bước này.
        body = registry.load_body(skill)
        rows.append([
            skill.name,
            len(skill.meta_text),
            estimate_tokens(skill.meta_text),
            len(body),
            estimate_tokens(body),
        ])
    print_table(
        ["Skill", "Meta (ký tự)", "Meta token", "Body (ký tự)", "Body token"],
        rows, widths=[12, 12, 10, 12, 10],
    )

    meta_total = registry.metadata_tokens()
    body_total = sum(estimate_tokens(registry.load_body(s)) for s in registry.skills)
    print(f"\n[chi phí] Metadata mọi skill: {meta_total} token.")
    print(f"[chi phí] Nếu nhồi toàn văn mọi skill vào system: {meta_total + body_total} token mỗi request.")

    queries = [
        "Khách đòi hoàn tiền cho đơn 1234 vì tai nghe bị rè",
        "Review câu SQL này giúp mình, có bị N+1 không",
        "Làm sao đổi mật khẩu tài khoản?",
    ]

    print("\n[tra cứu]")
    used = 0
    rows = []
    for query in queries:
        skill = registry.match(query)
        if skill is None:
            cost = meta_total
            used += cost
            rows.append([shorten(query, 34), "—", cost, meta_total + body_total, "không nạp body"])
            continue
        body = registry.load_body(skill)
        cost = meta_total + estimate_tokens(body)
        used += cost
        rows.append([
            shorten(query, 34), skill.name, cost, meta_total + body_total,
            f"tiết kiệm {meta_total + body_total - cost}",
        ])
        print(f"\n  Khớp '{skill.name}' → nạp thân bài ({estimate_tokens(body)} token):")
        for line in body.splitlines()[:6]:
            print("   ", line)
        print("    ...")

    print()
    print_table(
        ["Câu hỏi", "Skill nạp", "Token dùng", "Nếu nạp tất cả", "Ghi chú"],
        rows, widths=[34, 11, 10, 15, 18],
    )
    naive = len(queries) * (meta_total + body_total)
    print(f"\n[done] 3 request: {used} token (progressive) so với {naive} token (nhồi tất cả).")
    print(f"       Tiết kiệm {naive - used} token, tức {(naive - used) * 100 // naive}%.")


if __name__ == "__main__":
    main()
