# *heuristic_analysis*

#### Brief Introduction for every heuristic function:

(For convenience, mark *heuristic_func1* `1`, *heuristic_func_2* `2`, and so on.)

`1` is exactly improved_score, which is the difference in the number of moves availuable to the two players

`2` is the difference between the number of player's potentially reachable moves and that of its opponent(this function involves breadth-first search, so it comes with higher time cost)

`3` combines both above. return the max value of them.

`4` calls `1` when there are more than half number of spaces on the board blank, and calls `2` when there are less.

`5` and `6` are almost the same as `4`, with different timing (1/3 board filled, 2/3 board filled) to switch from `1` to `2`

#### Results

After running three times for each heuristic function. here is what I got. The data represent winning rates

| winning rate (%) | `1`   | `2`   | `3`   | `4`   | `5`   | `6`   |
| ---------------- | ----- | ----- | ----- | ----- | ----- | ----- |
| *Round 1*        | 69.29 | 67.14 | 69.29 | 72.14 | 70.00 | 70.00 |
| *Round 2*        | 68.57 | 62.14 | 72.14 | 76.43 | 70.00 | 75.00 |
| *Round 3*        | 65.00 | 62.86 | 67.86 | 72.86 | 72.14 | 70.71 |

#### Further analysis

The best choice seems `4` from the tests. `3`, `4`, `5` and `6` all combine `1` and `2`. I thought `3` was supposed to be the best choice in the first place. But since it invokes `reachable_postion_counter` every time which comes with higher time cost, it causes iterative deepening search down shallower than others. And that ends up reducing its accuracy. In light of the fact that `2` is around *0* at the beginning of the game(reachable positions for both players are almost equal at that time), I came up with the idea which invokes `1` at the beginning of the game and switches to `2` as there are fewer blanks. In this way, the timing to switch becomes crucial, and that's where `4`, `5` and `6` come from. From the results above, it seems that `4` is the best choice.