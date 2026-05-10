"""游戏逻辑测试 — 数学题生成"""
import sys
import os
import random

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def _generate_question(difficulty, ops, max_val):
    """模拟数学题生成逻辑。"""
    if difficulty == "easy":
        a = random.randint(1, max_val)
        b = random.randint(1, max_val)
        op = random.choice(ops)
        if op == "+":
            answer = a + b
        else:
            if a < b:
                a, b = b, a
            answer = a - b
        question = f"{a}{op}{b}"
    elif difficulty == "normal":
        op = random.choice(ops)
        if op == "*":
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            answer = a * b
            question = f"{a}×{b}"
        else:
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            if op == "-" and a < b:
                a, b = b, a
            answer = a + b if op == "+" else a - b
            question = f"{a}{op}{b}"
    else:  # hard
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(1, 5)
        op1 = random.choice(["+", "-"])
        op2 = random.choice(["+", "-"])
        if op1 == "-" and a < b:
            a, b = b, a
        inner = a + b if op1 == "+" else a - b
        answer = inner * c
        question = f"({a}{op1}{b})×{c}"

    # 生成错误答案
    wrong = set()
    while len(wrong) < 3:
        offset = random.randint(-5, 5)
        wrong_ans = answer + offset
        if wrong_ans != answer and wrong_ans >= 0:
            wrong.add(wrong_ans)

    return question, answer, list(wrong)


def test_easy_range():
    """简单难度数值在合理范围。"""
    for _ in range(50):
        _, answer, wrong = _generate_question("easy", ["+", "-"], 10)
        assert 0 <= answer <= 20, f"答案超出范围: {answer}"
    print("  [PASS] test_easy_range")


def test_normal_range():
    """普通难度数值在合理范围。"""
    for _ in range(50):
        _, answer, wrong = _generate_question("normal", ["+", "-", "*"], 20)
        assert 0 <= answer <= 50, f"答案超出范围: {answer}"
    print("  [PASS] test_normal_range")


def test_hard_range():
    """困难难度数值在合理范围。"""
    for _ in range(50):
        _, answer, wrong = _generate_question("hard", ["+", "-"], 50)
        assert 0 <= answer <= 100, f"答案超出范围: {answer}"
    print("  [PASS] test_hard_range")


def test_has_exactly_one_correct():
    """只有一个正确答案。"""
    for _ in range(50):
        question, answer, wrong = _generate_question("easy", ["+", "-"], 10)
        assert answer not in wrong, f"错误答案中包含正确答案: {question} -> {answer}"
    print("  [PASS] test_has_exactly_one_correct")


def test_wrong_answers_are_wrong():
    """错误答案确实不等于正确答案。"""
    for _ in range(50):
        _, answer, wrong = _generate_question("normal", ["+", "-", "*"], 20)
        for w in wrong:
            assert w != answer, f"错误答案等于正确答案: {answer}"
    print("  [PASS] test_wrong_answers_are_wrong")


def test_no_duplicate_answers():
    """所有选项互不相同。"""
    for _ in range(50):
        _, answer, wrong = _generate_question("hard", ["+", "-"], 50)
        all_answers = [answer] + wrong
        assert len(all_answers) == len(set(all_answers)), "存在重复答案"
    print("  [PASS] test_no_duplicate_answers")


if __name__ == "__main__":
    print("Running math question generation tests...")
    test_easy_range()
    test_normal_range()
    test_hard_range()
    test_has_exactly_one_correct()
    test_wrong_answers_are_wrong()
    test_no_duplicate_answers()
    print("\nAll math question tests passed!")
