"""Zero-shot prompts for each benchmark, and the answer line each one requires.

The prompts are EvalScope's, verbatim (benchmarks/*_adapter.py and
utils/multi_choices.py), so an instruction-tuned model is asked the same way
a chat model is evaluated. Every prompt asks the model to think step by step
and finish with a fixed last line: 'ANSWER: X', or '答案：X' for C-Eval.
"""

import re

LETTERS = "ABCDEFGHIJ"

# MMLU-Pro adapter.
MMLU_PRO = (
    "Answer the following multiple choice question. The last line of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}. Think step by step before answering.\n\n"
    "Question:\n{question}\nOptions:\n{choices}\n"
)
# MultipleChoiceTemplate.SINGLE_ANSWER_COT: MMLU-Redux, SuperGPQA, GPQA.
SINGLE_ANSWER_COT = (
    "Answer the following multiple choice question. The last line of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}. Think step by step before answering.\n\n"
    "{question}\n\n{choices}"
)
# C-Eval adapter.
CEVAL = (
    "以下是中国关于{subject}的单项选择题，请选出其中的正确答案。你的回答的最后一行应该是这样的格式："
    '"答案：[LETTER]"（不带引号），其中 [LETTER] 是 A、B、C、D 中的一个。\n\n'
    "问题：{question}\n选项：\n{choices}\n"
)
CEVAL_SUBJECTS = {
    "computer_network": "计算机网络",
    "operating_system": "操作系统",
    "computer_architecture": "计算机组成",
    "college_programming": "大学编程",
    "college_physics": "大学物理",
    "college_chemistry": "大学化学",
    "advanced_mathematics": "高等数学",
    "probability_and_statistics": "概率统计",
    "discrete_mathematics": "离散数学",
    "electrical_engineer": "注册电气工程师",
    "metrology_engineer": "注册计量师",
    "high_school_mathematics": "高中数学",
    "high_school_physics": "高中物理",
    "high_school_chemistry": "高中化学",
    "high_school_biology": "高中生物",
    "middle_school_mathematics": "初中数学",
    "middle_school_biology": "初中生物",
    "middle_school_physics": "初中物理",
    "middle_school_chemistry": "初中化学",
    "veterinary_medicine": "兽医学",
    "college_economics": "大学经济学",
    "business_administration": "工商管理",
    "marxism": "马克思主义基本原理",
    "mao_zedong_thought": "毛泽东思想和中国特色社会主义理论体系概论",
    "education_science": "教育学",
    "teacher_qualification": "教师资格",
    "high_school_politics": "高中政治",
    "high_school_geography": "高中地理",
    "middle_school_politics": "初中政治",
    "middle_school_geography": "初中地理",
    "modern_chinese_history": "近代史纲要",
    "ideological_and_moral_cultivation": "思想道德修养与法律基础",
    "logic": "逻辑学",
    "law": "法学",
    "chinese_language_and_literature": "中国语言文学",
    "art_studies": "艺术学",
    "professional_tour_guide": "导游资格",
    "legal_professional": "法律职业资格",
    "high_school_chinese": "高中语文",
    "high_school_history": "高中历史",
    "middle_school_history": "初中历史",
    "civil_servant": "公务员",
    "sports_science": "体育学",
    "plant_protection": "植物保护",
    "basic_medicine": "基础医学",
    "clinical_medicine": "临床医学",
    "urban_and_rural_planner": "注册城乡规划师",
    "accountant": "注册会计师",
    "fire_engineer": "注册消防工程师",
    "environmental_impact_assessment_engineer": "环境影响评价工程师",
    "tax_accountant": "税务师",
    "physician": "医师资格",
}

ANSWER_LINE = re.compile(r"ANSWER:\s*([A-J])\s*")
ANSWER_LINE_ZH = re.compile(r"答案：\s*([A-D])\s*")
ANSWER_ANYWHERE = re.compile(r"(?i)ANSWER\s*:\s*\**\s*\(?([A-J])\b")
ANSWER_ANYWHERE_ZH = re.compile(r"答案\s*[:：]\s*\**\s*([A-D])")


def user_prompt(item):
    """The user message for a benchmark item from `memorize.benchmarks`."""
    n = len(item["options"])
    bench = item["benchmark"]
    if bench == "ceval":
        return CEVAL.format(
            subject=CEVAL_SUBJECTS[item["subject"]],
            question=item["question"],
            choices="\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(item["options"])),
        )
    template = MMLU_PRO if bench == "mmlu_pro" else SINGLE_ANSWER_COT
    return template.format(
        letters=",".join(LETTERS[:n]),
        question=item["question"],
        choices="\n".join(f"{LETTERS[i]}) {o}" for i, o in enumerate(item["options"])),
    )


def strict_answer(text, bench):
    """The letter on the last non-empty line if that line is exactly the
    required answer line, else None. This is the format the RL reward uses."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None
    m = (ANSWER_LINE_ZH if bench == "ceval" else ANSWER_LINE).fullmatch(lines[-1])
    return m.group(1) if m else None


def loose_answer(text, bench):
    """The last answer marker anywhere in the reply, however it is formatted."""
    found = (ANSWER_ANYWHERE_ZH if bench == "ceval" else ANSWER_ANYWHERE).findall(text)
    return found[-1].upper() if found else None
