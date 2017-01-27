In short, we created a 'mats' dictionary that held all necessary items to achieve the goal.
Our search/heuristic we wanted included this 'mats' to be mutated through each state as long as the state we're currently examining created something that we need. 

We wanted to stick to a simple rule. "If we didn't need it, we don't want it".

If the state didn't create something in our 'mats' dictionary there is no point to even consider this state and thus wouldn't be appended into our queue. A difficult part we encountered was how to exactly calculate the heuristic and it is still an issue with our program today. We know that if we want the item that this state produces, then we should ultimately choose it, but there are other paths that also include items in 'mats'.

