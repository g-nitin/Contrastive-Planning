def _single_ques_prompt(problem, solution, question, action, preconditions_action, effects_action) -> str:
    """
    Helper function to generate a prompt for a single question.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param question: The question to be answered.
    @param action: The specific action mentioned in the question.
    @param preconditions_action: The preconditions of the action.
    @param effects_action: The effects of the action.
    @return: A formatted prompt string.
    """

    return f"""
    I have a Sokoban problem with the following initial and goal states expressed in PDDL:

    **Initial and Goal States:**
    ```
    {problem}
    ```

    **Generated Solution Plan:**
    ```
    {solution}
    ```

    I need you to answer the following question concisely by reasoning through the provided information:

    **Question:**
    ```
    {question}
    ```

    For context, here is additional information about the specific action mentioned in the question:

    **Action:**
    ```
    {action}
    ```

    **Preconditions of the Action:**
    ```
    {preconditions_action}
    ```

    **Effects of the Action:**
    ```
    {effects_action}
    ```

    Using this information, please provide a short, logical response that addresses the question.
    """


def _double_ques_prompt(problem, solution, question, action_1, preconditions_1, effects_1,
                        action_2, preconditions_2, effects_2) -> str:
    """
    Helper function to generate a prompt for a question with two actions.
    @param problem: The Sokoban problem in PDDL format.
    @param solution: The generated solution plan.
    @param question: The question to be answered.
    @param action_1: The first specific action mentioned in the question.
    @param preconditions_1: The preconditions of the first action.
    @param effects_1: The effects of the first action.
    @param action_2: The second specific action mentioned in the question.
    @param preconditions_2: The preconditions of the second action.
    @param effects_2: The effects of the second action.
    @return: A formatted prompt string.
    """

    return f"""
    I have a Sokoban problem with the following initial and goal states expressed in PDDL:

    **Initial and Goal States:**
    ```
    {problem}
    ```

    **Generated Solution Plan:**
    ```
    {solution}
    ```

    I need you to answer the following question concisely by reasoning through the provided information:

    **Question:**
    ```
    {question}
    ```

    For context, here is additional information about the specific actions mentioned in the question:

    **Action 1:**
    ```
    {action_1}
    ```

    **Preconditions of the 1st Action:**
    ```
    {preconditions_1}
    ```

    **Effects of the 1st Action:**
    ```
    {effects_1}
    ```
    
    **Action 2:**
    ```
    {action_2}
    ```

    **Preconditions of the 2nd Action:**
    ```
    {preconditions_2}
    ```

    **Effects of the 2nd Action:**
    ```
    {effects_2}
    ```

    Using this information, please provide a short, logical response that addresses the question.
    """


def get_problem() -> str:
    return """
        (define (problem sokoban)
            (:domain sokoban)
            (:objects sokoban crate1 crate2 l1 l10 l11 l12 l17 l18 l19 l22 l23 l24 l29 l30 l31 l32 l33 l36 l37 l38 l39 l40)
            (:init (sokoban sokoban)
                (crate crate1)
                (crate crate2)
                (leftOf l10 l11)
                (leftOf l11 l12)
                (leftOf l17 l18)
                (leftOf l18 l19)
                (leftOf l22 l23)
                (leftOf l23 l24)
                (leftOf l29 l30)
                (leftOf l30 l31)
                (leftOf l31 l32)
                (leftOf l32 l33)
                (leftOf l36 l37)
                (leftOf l37 l38)
                (leftOf l38 l39)
                (leftOf l39 l40)
                (below l17 l10)
                (below l18 l11)
                (below l19 l12)
                (below l24 l17)
                (below l29 l22)
                (below l30 l23)
                (below l31 l24)
                (below l36 l29)
                (below l37 l30)
                (below l38 l31)
                (below l39 l32)
                (below l40 l33)
                (at sokoban l19)
                (at crate1 l17)
                (at crate2 l18)
                (clear l1)
                (clear l10)
                (clear l11)
                (clear l12)
                (clear l22)
                (clear l23)
                (clear l24)
                (clear l29)
                (clear l30)
                (clear l31)
                (clear l32)
                (clear l33)
                (clear l36)
                (clear l37)
                (clear l38)
                (clear l39)
                (clear l40)
            )
            (:goal (and
                (or (at crate1 l37) (at crate2 l37) )
                (or (at crate1 l39) (at crate2 l39) )
            ))
        )
        """


def get_solution() -> str:
    return """
    (moveup sokoban l19 l12)
    (moveleft sokoban l12 l11)
    (moveleft sokoban l11 l10)
    (pushdown sokoban l10 l17 l24 crate1)
    (pushdown sokoban l17 l24 l31 crate1)
    (moveleft sokoban l24 l23)
    (movedown sokoban l23 l30)
    (movedown sokoban l30 l37)
    (moveright sokoban l37 l38)
    (moveright sokoban l38 l39)
    (moveup sokoban l39 l32)
    (pushleft sokoban l32 l31 l30 crate1)
    (moveup sokoban l31 l24)
    (moveup sokoban l24 l17)
    (moveup sokoban l17 l10)
    (moveright sokoban l10 l11)
    (moveright sokoban l11 l12)
    (movedown sokoban l12 l19)
    (pushleft sokoban l19 l18 l17 crate2)
    (moveup sokoban l18 l11)
    (moveleft sokoban l11 l10)
    (pushdown sokoban l10 l17 l24 crate2)
    (pushdown sokoban l17 l24 l31 crate2)
    (pushdown sokoban l24 l31 l38 crate2)
    (moveup sokoban l31 l24)
    (moveleft sokoban l24 l23)
    (moveleft sokoban l23 l22)
    (movedown sokoban l22 l29)
    (movedown sokoban l29 l36)
    (moveright sokoban l36 l37)
    (pushright sokoban l37 l38 l39 crate2)
    (moveup sokoban l38 l31)
    (moveup sokoban l31 l24)
    (moveleft sokoban l24 l23)
    (pushdown sokoban l23 l30 l37 crate1)
    """


def prompt_1() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x used in the solution?
    @return: A formatted prompt string.
    """

    problem: str = get_problem()
    solution: str = get_solution()

    action: str = "moveup sokoban l39 l32"

    # Additional information about the specific action mentioned in the question
    # From `code/sokoban_exploration/sokoban_explore.ipynb`
    preconditions: list[str] = ['sokoban sokoban', 'at sokoban l39', 'below l39 l32', 'clear l32']
    effects: list[str] = ['at sokoban l32', 'clear l39', 'not (at sokoban l39)', 'not (clear l32)']

    question: str = f"Why is the action {action} used in the solution?"

    return _single_ques_prompt(problem, solution, question, action, preconditions, effects)


def prompt_2() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x not used in the solution?
    @return: A formatted prompt string.
    """

    problem: str = get_problem()
    solution: str = get_solution()

    action: str = "pushdown sokoban l23 l30 l37 crate1"

    # Additional information about the specific action mentioned in the question
    # From `code/sokoban_exploration/sokoban_explore.ipynb`
    preconditions: list[str] = ['sokoban sokoban', 'crate crate1', 'below l30 l23',
                                'below l37 l30', 'at sokoban l23', 'at crate1 l30', 'clear l37']
    effects: list[str] = ['at sokoban l30', 'at crate1 l37', 'clear l23', 'not (at sokoban l23)',
                          'not (at crate1 l30)', 'not (clear l30)', 'not (clear l37)']

    question: str = f"Why is the action {action} not used in the solution in the last step?"

    return _single_ques_prompt(problem, solution, question, action, preconditions, effects)


def prompt_3() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x used in the solution instead of action w?
    @return: A formatted prompt string.
    """

    problem: str = get_problem()
    solution: str = get_solution()

    action1: str = "pushdown sokoban l10 l17 l24 crate1"
    preconditions_1: list[str] = ['sokoban sokoban', 'crate crate1', 'below l17 l10',
                                  'below l24 l17', 'at sokoban l10', 'at crate l17', 'clear l24']
    effects_1: list[str] = ['at sokoban l17', 'at crate1 l24', 'clear l10', 'not (at sokoban l10)',
                            'not (at crate1 l17)', 'not (clear l17)', 'not (clear l24)']

    action2: str = "pushup sokoban l10 l17 l24 crate1"
    preconditions_2: list[str] = ['sokoban sokoban', 'crate crate1', 'below l10 l17', 'below l17 l24',
                                  'at sokoban l10', 'at crate1 l17', 'clear l24']
    effects_2: list[str] = ['at sokoban l17', 'at crate1 l24', 'clear l10',
                            'not (at sokoban l10)', 'not (at crate1 l17)', 'not (clear l17)', 'not (clear l24)']

    question: str = f"For the last step, why is the action {action1} used in the solution rather than action {action2}?"

    return _double_ques_prompt(problem, solution, question,
                               action1, preconditions_1, effects_1, action2, preconditions_2, effects_2)
