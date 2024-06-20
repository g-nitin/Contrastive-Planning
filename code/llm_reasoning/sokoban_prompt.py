problem_1: str = """
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

solution_1: str = """
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

action: str = "moveup"
question_1: str = f"Why is the action {action} used in the solution?"

preconditions_action: list[str] = ['sokoban ?sokoban', 'at ?sokoban ?x', 'below ?x ?y', 'clear ?y']
effects_action: list[str] = ['at ?sokoban ?y', 'clear ?x', 'not (at ?sokoban ?x)', 'not (clear ?y)']

prompt_1: str = f"""
I have a Sokoban problem with the following initial and goal states expressed in PDDL:

**Initial and Goal States:**
```
{problem_1}
```

**Generated Solution Plan:**
```
{solution_1}
```

I need you to answer the following question concisely by reasoning through the provided information:

**Question:**
```
{question_1}
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
