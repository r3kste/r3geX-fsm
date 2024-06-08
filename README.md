# r3geX-fsm

## Introduction

This is a simple regex engine using FSM
(Finite State Machine). Currently, it supports the following features:

- Direct Matches

- Wildcard Character

- Special Characters: `*`, `+`, `?`, `^`, `$`

- Multiple Matches

- Character Sets, Negated Character Sets and Ranges

- All Escape Characters

- Alternation `|`

## Implementation

### FSM

To quote from the
[Wikipedia](https://en.wikipedia.org/wiki/Finite-state_machine) article
on FSM:

> A Finite State Machine (FSM) is a mathematical model of computation.
> It is an abstract machine that can be in exactly one of a finite
> number of states at any given time. The FSM can change from one state
> to another in response to some inputs; the change from one state to
> another is called a transition. An FSM is defined by a list of its
> states, its initial state, and the conditions for each transition.

This doesn't help much, so let's look at a simple example, that is
relevant to regular expression matching.

### Direct Match

Consider the regular expression `abcd`. This is a direct match, i.e., it
matches exactly for the string `abcd`. We can represent this as a FSM,
as shown below:

![FSM for the regular expression
`abcd`](/images/abcd.png)

In this, we have 6 states. The first one is the 'Start' and the final
one is the 'End'. We will have one pointer that will move from one state
to another, based on the input string. If at any point, the pointer
reaches the 'END' state, then it means that we have a match.

This works in the following manner:

1. The pointer starts at the 'START' state.

2. If the FSM encounters the character 'a', then it moves to the next
    state (S1).

3. In this new state, the FSM checks for the character 'b'. If it is
    'b', then it moves to the next state (S2). If it is not 'b', then
    the FSM resets to the 'START' state.

4. This process continues until the pointer reaches the 'END' state. If
    the pointer reaches the 'END' state, then it means that we have a
    match.

This is the simplest of the FSMs, and we can build upon this to match
more complex regular expressions.

### The Asterisk

In regex, the asterisk (\*) is used to match zero or more occurrences of
the preceding character. For example, the regex `ab*c` will match `ac`,
`abc`, `abbc`, etc.

One of the simplest ways to implement this is to use a self-loop in the
FSM. This means that the current state can loop back to itself, if the
character matches. This is shown in the figure below:

![FSM for the regular expression
`ab*c`](/images/ab8c.png)

If the FSM gets the character `a`, it transitions to S1. At this state,
the FSM can either move to the next state (S2) for the character 'c', or
it can loop back to the same state for the character 'b'. This way, the
FSM can match any number of 'b's, and then finally match 'c'. If the FSM
encounters any other character, then it resets to the 'START' state.

### Wildcards and other Special Characters

Regex has some special characters. For example:

1. `.` - The **dot** or **Wildcard** can match any character. For
    example, the regex `ab.d` will match `abcd`, `abbd`, `abzd`, etc.

    The implementation of the dot, is pretty simple. We can just add an
    edge corresponding to the dot, from the current state to the next
    state. We can check for the dot using a simple if condition within
    `FSM.match` function.

    ![FSM for the regular expression `ab.d`](/images/ab.d.png)

2. `+` - The **plus** matches one or more occurrences of the preceding
    character. For the `+`, observe that it is somewhat similar to the
    implementation of `*`, that we did earlier. Instead of a self-loop
    to the current state like in the case of `*`, we can add the
    self-loop to a new state. This will make it equivalent to using with
    the `*`. For example, `ab+c` will be equivalent to `abb*c`.

    ![FSM for the regular expression `ab+c`](/images/ab+c.png)

3. `?` - The **question mark** matches zero or one occurrence of the
    preceding character. Implementation of the `?` is also simple. We
    can have two transitions from the current state, one for the one
    occurrence and one for zero occurrences.

    ![FSM for the regular expression `ab?c`](/images/ab%3Fc.png)

4. `^` and `$` - The **caret** matches the start of the string, and the
    **dollar** matches the end of the string. For `^` and `$`, it is
    simpler to check the start and end of the string during matching
    (like in the case of the Wildcard operator: `.`), rather than
    building a FSM for it.

    ![FSM for the regular expression `^ab$`](/images/^ab$.png)

### Character Sets

Character sets are used to match any one of the characters within the
square brackets. For example, the regex `[abc]` will match any one of
the characters `a`, `b` or `c`. We can implement this by adding multiple
transitions from the current state to the next state, for each character
in the set.

But before that, we need to keep in mind that there are also ranges in
character sets. For example, `[a-z]` will match any character from `a`
to `z`. One way to implement this is by having 26 transitions from the
current state to the next state, for each character in the range.
However, this is not very memory efficient. Moreover, we also need to
handle negated character sets like `[^a-z]`.

In order to implement this:

- I created another class `Token`. A `Token`, is the smallest unit in
    the regex engine. It can be a character, a wildcard, a range, etc.

- It has an attribute `negated`, which is `True` if the token is
    negated.

- Until now, we have been using characters to build our transitions.
    Now, we will use `Tokens`, which gives us a lot more flexibility,
    and makes the implementation easier in the cases of Negated
    Character Sets and Ranges.

- Tokens also solve the problem where a new transition with the same
    character overwrites the previous transition. This doesn't happen
    with Tokens, as they are unique objects. This allows us to have
    multiple transitions for the same character from the same state.

Coming back to character sets, it was done in a simple way, as there can
be no nesting or special characters within the character set. I just
added each element of the set as a `Token` and added transitions for
each of them, where all of them lead to the same state.

![FSM for the regular expression
`[aeiou]`](/images/[aeiou].png)

The best part about this is that, becuase ranges are also `Tokens`, they
will now work with special characters like `.`, `*`, etc. For example,
the regex `[a-z]*` will match any string that has only lowercase
alphabets.

![FSM for the regular expression
`[a-z]*`](/images/[a-z]8.png)

### Escape from Reality

In regex, escaped characters are used to match special characters. For
example, will match the character `*`, instead of matching zero or more
occurrences of the preceding character. This is easy to implement, as we
can just add an attribute `escaped` to the `Token` class, and check for
it in the `match` function. The Escape Characters that I implemented
are:

- `\w` - Matches any word character or underscore. It is equivalent to
    `[a-zA-Z0-9_]`.

- `\W` - Matches any non-word character and non-underscores. It is
    equivalent to `[^a-zA-Z0-9_]`.

- `\d` - Matches any digit. It is equivalent to `[0-9]`.

- `\D` - Matches any non-digit. It is equivalent to `[^0-9]`.

- `\s` - Matches any whitespace character such as spaces, tabs and
    line breaks.

- `\S` - Matches any non-whitespace character.

- `\b` - Matches a word boundary.

- `\B` - Matches a non word-boundaries.

I also added a few more Escape characters (that are not very common):

- `\t` - Matches a tab character.

- `\n` - Matches a newline character.

- `\v` - Matches a vertical tab character.

- `\f` - Matches a form feed character.

- `\r` - Matches a carriage return character.

With this, we can finally do something useful, such as
`[\w]+@[\w]+\.[\w]+`. This regular expression can match basic email
addresses.

### Alternation

The `|` character acts like a boolean OR. For example, the regex
`good|bad` will match either `good` or `bad`. This is simple to
implement. Assuming that the regular expression doesn't have any
parantheses, we can just split the regex at the `|` character, and build
the FSM for each part. We can then merge the FSMs by adding transitions
from the START state to the FSMs of each part. Of course, we have to
consider the case where the `|` character is escaped, in which case it
should be treated as a normal character.

### Multiple Matches

In order to match multiple occurrences, I implemented the `match`
function in such a way that it has one or more pointers.

- I first go through the string and check if a character is directly
    connected to the START state. This means that, the character is
    valid start for a pattern.

- With this list of pointers, I select one pointer at a time, and move
    it through the FSM. If at any point, there are more than one valid
    transitions, then I create a new pointer for each transition. This
    way, I can match multiple occurrences.

- In a way, I am basically traversing the FSM using **Depth First
    Search (DFS)**. I keep track of the pointers that are valid at each
    step, and move them accordingly.

- Note that, I have only one moving pointer at any given time,
    although I have a list of valid pointers. This particular pointer
    either reaches the END state if it is a valid match, else it is
    discarded, and we start using the next valid pointer. This satisfies
    the condition that the FSM can be in exactly one state at any given
    time.

- I maintain a list of valid matches. If a pointer reaches the END
    state, then I add the start and end index of the match to the list.
    After the list of all pointers is exhausted, I return this list of
    valid matches.

- The indices within this list, are part of the match. I used the
    python library `termcolor` to highlight the matches in the string.

## Code

Throughout the implementation, I am working with the FSM by considering
it as a directed graph. Each node in the graph is a `State` and each
edge corresponds to a transition. The transitions are stored in a
dictionary, where the key is a `Token`, and the value is the next state.

### Imports

I used `graphviz` to plot the FSMs, and `termcolor` to highlight the
matches in the string.

### FSM

The whole implementation is done within the `FSM` class. The class has
some subclasses like `Token` and `State`.

#### Token

The `Token`, as mentioned earlier, is the smallest unit in the regex
engine. It can be a character, a wildcard, a range, etc. It has
attributes like `negated` and `escaped`. The `__repr__` function is used
to represent the token in a human-readable format.

The `FSM.Token` class has one function `__contains__`, which is used to
check if a character is in the range of the token. It returns a boolean
value which depends on the `negated` attribute.

#### State

The `State` class is used to represent a node in the FSM. It has
attributes like `is_start` and `is_end`. Most Importantly, It has the
dictionary `transitions`, which stores the transitions from the current
state to the next state. The `__repr__` function is used to represent
the state in a human-readable format.

The `FSM.State` class has a function `link`, which is used to add a
transition from the current state to the target state.

#### FSM Functions

Now, the functions of the `FSM` class are explained here:

- `split_and_compile`: This function splits the regular expression at
    the `|` character, and compiles the FSM for each part. It then
    merges the FSMs by linking these FSMs with the START and END state
    by calling the `FSM.compile` function. It also takes care of cases
    where the `|` character is escaped.

- `compile`: This function is used to compile the FSM for a given
    regular expression. It does this by going through the regular
    expression character by character, and building the FSM accordingly.
    This is the heart of the regex engine. It uses subfunctions like
    `build` and `link` to build the FSM. Its functioning is explained
    here:

  - `FSM.compile.build`: This function looks at the next character
        in the regular expression, and decides how to link the current
        state to the next state. It uses the `link` function to add the
        transitions.

  - `FSM.compile.link`: This function is used to add transitions
        from the current state to the target state. It also takes care
        of adding transitions for multiple parents. The cases of
        multiple parents arise when we have operators such as `*`, and
        `?` which can have zero occurrences. This means that the state
        before these can also lead to the target state. Therefore, the
        states before the `current` state are maintained in a list
        called `parents`.

  - With the help of these functions, a forward pass is made through
        the regular expression, and the FSM is built accordingly,
        considering features like **Character Sets**, **Negated
        Character Sets**, **Ranges**, **Escaped Characters**, etc.

  - Finally, the function adds transitions from the `parents` and
        `current` state to the `END` state.

- `match`: This function is used to match the regular expression with
    a given string. Its functioning is explained here:

  - It maintains a list of valid pointers, and moves them through
        the FSM. If a pointer reaches the END state, then it is added to
        the list of valid matches. The indices of these matches are then
        returned.

  - It also implements the `^` and `$` characters, by checking for
        these transitions at the start and end of the string.

  - The function has a subfunction `FSM.match.transition` which
        looks at the current character in the string and all the
        transitions from the current state, and moves the pointer
        accordingly. This is the function that implements the **Depth
        First Search (DFS)**. Some examples are:

    - If the transition is `\d` and the current character is a
            digit, then the pointer moves to the corresponding state.

    - If there is a transition for the character `.`, then the
            pointer moves to the corresponding state, irrespective of
            the current character.

- `plot`: Finally, I have a function to plot the FSM. This function
    uses the `Graphviz` library to plot the FSM. It uses the `Digraph`
    class to create the directed graph, and adds the nodes and edges
    accordingly. The function then saves the graph as a `.png` file.

### Usage

``` {caption="Usage"}
regexp = input("Regular Expression: ")
fsm = FSM(regexp)

string = input("Sample string: ")
matches = fsm.match(string)
highlighted = highlight(string, matches)

print(highlighted)
fsm.plot(view=True)
```

## Some FSMs

Here are the FSMs for some of the regular expressions that I tested:

![FSM for the regular expression
`abcd`](/images/abcd.png)

![Direct Match](/images/t1.png)

![FSM for the regular expression `a*c*`](/images/a8c8.png)

![Any Number of 'a's and 'c's](/images/t2.png)

![FSM for the regular expression `a*`](/images/a8.png)

![Multiple Matches](/images/t3.png)

![FSM for matching simple email addresses](/images/emaill.png)

![Matched Email Address](/images/email.png)

![FSM for matching vowels](/images/[aeiouAEIOU].png)

![Matched Vowels](/images/vowel.png)

![FSM for \[\^a-z\]](/images/[^a-z].png)

![Matches for non-lowercase
alphabets](/images/notlower.png)

![FSM for the regular expression
`awesome|great`](/images/awesome|great.png)

![Alternation](/images/alter.png)

### Greedy Matches

One interesting thing that I learnt while implementing the regex engine
is that, the engine is **greedy**.

It is shown in the examples below:

![image](/images/greedyregex1.png)

![image](/images/greedyregex2.png)

![image](/images/greedyregex3.png)

![image](/images/greedyregex4.png)

We can notice in the second example, that the engine **does not** match
the string. This is because the first two `a`'s are **used** in matching
the pattern. As the engine is `greedy`, it now will not consider the
second `a` as a valid start for the pattern. Therefore, it **does not**
match the middle part of the string.
