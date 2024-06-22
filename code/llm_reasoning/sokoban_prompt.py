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


def prompt_1() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x used in the solution?
    @return: A formatted prompt string.
    """

    problem: str = """
    (define (problem s1)
        (:domain sokoban)
        (:objects sokoban, crate2, l1, l2, l5, l6, l9, l10, l11, l12, l13, l14, l15, l16, l17, l18)
        (:init (sokoban sokoban) 
               (crate crate2)

               ;;horizontal relationships
               (leftOf l1 l2) 
               (leftOf l5 l6) 
               (leftOf l9 l10) (leftOf l10 l11) (leftOf l11 l12) 
               (leftOf l13 l14) (leftOf l14 l15) (leftOf l15 l16)
               (leftOf l17 l18)

               ;;vertical relationships
               (below l5 l1) (below l6 l2)
               (below l9 l5) (below l10 l6)
               (below l13 l9) (below l14 l10) (below l15 l11) (below l16 l12)
               (below l17 l13) (below l18 l14)

               ;;initialize sokoban and crate
               (at sokoban l10)
               (at crate2 l15) 

               ;;clear spaces
               (clear l1) 
               (clear l2) 
               (clear l5) 
               (clear l6) 
               (clear l9)
               (clear l11)
               (clear l12) 
               (clear l13) 
               (clear l14)
               (clear l16) 
               (clear l17)   				
               (clear l18))

        (:goal (and (at crate2 l2)))
    )
    """

    solution: str = """
    ((moveright sokoban l10 l11)
     (moveright sokoban l11 l12)
     (movedown sokoban l12 l16)
     (pushleft sokoban l16 l15 l14 crate2)
     (moveup sokoban l15 l11)
     (moveleft sokoban l11 l10)
     (moveleft sokoban l10 l9)
     (movedown sokoban l9 l13)
     (movedown sokoban l13 l17)
     (moveright sokoban l17 l18)
     (pushup sokoban l18 l14 l10 crate2)
     (pushup sokoban l14 l10 l6 crate2)
     (pushup sokoban l10 l6 l2 crate2))
    """

    action: str = "moveup sokoban l15 l11"

    # Additional information about the specific action mentioned in the question
    # From `code/sokoban_exploration/sokoban_explore.ipynb`
    preconditions: list[str] = ['sokoban sokoban', 'at sokoban l15', 'below l15 l11', 'clear l11']
    effects: list[str] = ['at sokoban l11', 'clear l15', 'not (at sokoban l15)', 'not (clear l11)']

    question: str = f"Why is the action {action} used in the solution?"

    return _single_ques_prompt(problem, solution, question, action, preconditions, effects)


def prompt_2() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x not used in the solution?
    @return: A formatted prompt string.
    """

    problem: str = """
    (define (problem s1)
        (:domain sokoban)
        (:objects sokoban, crate2, l1, l2, l5, l6, l9, l10, l11, l12, l13, l14, l15, l16, l17, l18)
        (:init (sokoban sokoban) 
               (crate crate2)

               ;;horizontal relationships
               (leftOf l1 l2) 
               (leftOf l5 l6) 
               (leftOf l9 l10) (leftOf l10 l11) (leftOf l11 l12) 
               (leftOf l13 l14) (leftOf l14 l15) (leftOf l15 l16)
               (leftOf l17 l18)

               ;;vertical relationships
               (below l5 l1) (below l6 l2)
               (below l9 l5) (below l10 l6)
               (below l13 l9) (below l14 l10) (below l15 l11) (below l16 l12)
               (below l17 l13) (below l18 l14)

               ;;initialize sokoban and crate
               (at sokoban l10)
               (at crate2 l15) 

               ;;clear spaces
               (clear l1) 
               (clear l2) 
               (clear l5) 
               (clear l6) 
               (clear l9)
               (clear l11)
               (clear l12) 
               (clear l13) 
               (clear l14)
               (clear l16) 
               (clear l17)   				
               (clear l18))

        (:goal (and (at crate2 l2)))
    )
    """

    solution: str = """
    ((moveright sokoban l10 l11)
     (moveright sokoban l11 l12)
     (movedown sokoban l12 l16)
     (pushleft sokoban l16 l15 l14 crate2)
     (moveup sokoban l15 l11)
     (moveleft sokoban l11 l10)
     (moveleft sokoban l10 l9)
     (movedown sokoban l9 l13)
     (movedown sokoban l13 l17)
     (moveright sokoban l17 l18)
     (pushup sokoban l18 l14 l10 crate2)
     (pushup sokoban l14 l10 l6 crate2)
     (pushup sokoban l10 l6 l2 crate2))
    """

    action: str = "pushdown sokoban l18 l14 l10 crate2"

    # Additional information about the specific action mentioned in the question
    # From `code/sokoban_exploration/sokoban_explore.ipynb`
    preconditions: list[str] = ['sokoban sokoban', 'crate crate2', 'below l14 l18',
                                'below l10 l14', 'at sokoban l18', 'at crate2 l14', 'clear l10']
    effects: list[str] = ['at sokoban l14', 'at crate2 l10', 'clear l18', 'not (at sokoban l18)',
                          'not (at crate2 l14)', 'not (clear l14)', 'not (clear l10)']

    question: str = f"Why is the action {action} not used in the solution for the third last step?"

    return _single_ques_prompt(problem, solution, question, action, preconditions, effects)


def prompt_3() -> str:
    """
    Generate a prompt for a Sokoban reasoning question.
    Question intent type: why is action x used in the solution instead of action w?
    @return: A formatted prompt string.
    """

    problem: str = """
    (define (problem s1)
        (:domain sokoban)
        (:objects sokoban, crate2, l1, l2, l5, l6, l9, l10, l11, l12, l13, l14, l15, l16, l17, l18)
        (:init (sokoban sokoban) 
               (crate crate2)

               ;;horizontal relationships
               (leftOf l1 l2) 
               (leftOf l5 l6) 
               (leftOf l9 l10) (leftOf l10 l11) (leftOf l11 l12) 
               (leftOf l13 l14) (leftOf l14 l15) (leftOf l15 l16)
               (leftOf l17 l18)

               ;;vertical relationships
               (below l5 l1) (below l6 l2)
               (below l9 l5) (below l10 l6)
               (below l13 l9) (below l14 l10) (below l15 l11) (below l16 l12)
               (below l17 l13) (below l18 l14)

               ;;initialize sokoban and crate
               (at sokoban l10)
               (at crate2 l15) 

               ;;clear spaces
               (clear l1) 
               (clear l2) 
               (clear l5) 
               (clear l6) 
               (clear l9)
               (clear l11)
               (clear l12) 
               (clear l13) 
               (clear l14)
               (clear l16) 
               (clear l17)   				
               (clear l18))

        (:goal (and (at crate2 l2)))
    )
    """

    solution: str = """
    ((moveright sokoban l10 l11)
     (moveright sokoban l11 l12)
     (movedown sokoban l12 l16)
     (pushleft sokoban l16 l15 l14 crate2)
     (moveup sokoban l15 l11)
     (moveleft sokoban l11 l10)
     (moveleft sokoban l10 l9)
     (movedown sokoban l9 l13)
     (movedown sokoban l13 l17)
     (moveright sokoban l17 l18)
     (pushup sokoban l18 l14 l10 crate2)
     (pushup sokoban l14 l10 l6 crate2)
     (pushup sokoban l10 l6 l2 crate2))
    """

    action1: str = "pushup sokoban l10 l6 l2 crate2"
    preconditions_1: list[str] = ['sokoban sokoban', 'crate crate2', 'below l10 l6', 'below l6 l2',
                                  'at sokoban l10', 'at crate2 l6', 'clear l2']
    effects_1: list[str] = ['at sokoban l6', 'at crate2 l2', 'clear l10',
                            'not (at sokoban l10)', 'not (at crate2 l6)', 'not (clear l6)', 'not (clear l2)']

    action2: str = "pushdown sokoban l12 l6 l2 crate2"
    preconditions_2: list[str] = [
        'sokoban sokoban', 'crate crate2', 'below l6 l12', 'below l2 l6', 'at sokoban l12', 'at crate l6', 'clear l2'
    ]
    effects_2: list[str] = ['at sokoban l6', 'at crate2 l2', 'clear l12', 'not (at sokoban l12)',
                            'not (at crate2 l6)', 'not (clear l6)', 'not (clear l2)']

    question: str = f"For the last step, why is the action {action1} used in the solution rather than action {action2}?"

    return _double_ques_prompt(problem, solution, question,
                               action1, preconditions_1, effects_1, action2, preconditions_2, effects_2)
