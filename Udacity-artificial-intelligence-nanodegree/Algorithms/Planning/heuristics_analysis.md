# Uninformed Planning Searches

| Problem |   Search    | Expansions | Goal Tests | New Nodes |  Time  | Plan Length |
| :-----: | :---------: | :--------: | :--------: | :-------: | :----: | :---------: |
|  `p1`   |  BFS[^BFS]  |     43     |     56     |    180    | 0.0396 |      6      |
|  `p2`   |     BFS     |    3343    |    4609    |   30509   | 16.430 |      9      |
|  `p3`   |     BFS     |   14663    |   18098    |  129631   | 115.76 |     12      |
|  `p1`   | DFGS[^DFGS] |     22     |     22     |    84     | 0.0175 |     20      |
|  `p2`   |    DFGS     |    624     |    625     |   5602    | 4.0012 |     619     |
|  `p3`   |    DFGS     |    408     |    409     |   3364    | 2.0989 |     392     |
|  `p1`   |  DLS[^DLS]  |    101     |    271     |    414    | 0.1136 |     50      |
|  `p2`   |     DLS     |   222719   |  2053741   |  2054119  | 1118.2 |     50      |
|  `p3`   |     DLS     |     -      |     -      |     -     |   -    |      -      |
|  `p1`   |  UCS[^UCS]  |     55     |     57     |    224    | 0.0457 |      6      |
|  `p2`   |     UCS     |    4852    |    4854    |   44030   | 14.844 |      9      |
|  `p3`   |     UCS     |   12559    |   12561    |  111601   | 66.984 |     12      |

[^BFS]: Breadth-First Search
[^DFGS]: Depth-First Graph Search
[^DLS]: Depth-Limited Search
[^UCS]: Uniform-Cost Search

> Optimal sequence of actions for `p1`: 
>
> 1. Load(C1, P1, SFO)
> 2. Load(C2, P2, JFK)
> 3. Fly(P2, JFK, SFO)
> 4. Unload(C2, P2, SFO)
> 5. Fly(P1, SFO, JFK)
> 6. Unload(C1, P1, JFK

> Optimal sequence of actions for `p2`:
>
> 1. Load(C1, P1, SFO)
> 2. Load(C2, P2, JFK)
> 3. Load(C3, P3, ATL)
> 4. Fly(P2, JFK, SFO)
> 5. Unload(C2, P2, SFO)
> 6. Fly(P1, SFO, JFK)
> 7. Unload(C1, P1, JFK)
> 8. Fly(P3, ATL, SFO)
> 9. Unload(C3, P3, SFO)

> Optimal sequence of actions for `p3`:
>
> 1. Load(C2, P2, JFK)
> 2. Fly(P2, JFK, ORD)
> 3. Load(C4, P2, ORD)
> 4. Fly(P2, ORD, SFO)
> 5. Unload(C4, P2, SFO)
> 6. Load(C1, P1, SFO)
> 7. Fly(P1, SFO, ATL)
> 8. Load(C3, P1, ATL)
> 9. Fly(P1, ATL, JFK)
> 10. Unload(C3, P1, JFK)
> 11. Unload(C2, P2, SFO)
> 12. Unload(C1, P1, JFK)

Apparently from the point of the given plans, *BFS* and *UCS* are better compared to other two searches. They always return the optimal plan. But they expand more nodes, do more goal test, and in turn take more time than *DFGS* in general cases. *UCS* is better than *BFS* for larger problems(like `p2` and `p3`). *DLS* is a disaster, it takes 'forever' to find a solution because it doens't check whether it meets a loop.

# Domain-Independent Heuristics

| Problem | Heuristic | Expansions | Goal Tests | New Nodes |  Time  | Plan Length |
| :-----: | :-------: | :--------: | :--------: | :-------: | :----: | :---------: |
|  `p1`   |  IP[^IP]  |     41     |     43     |    170    | 0.0451 |      6      |
|  `p1`   |  LS[^LS]  |     11     |     13     |    50     | 0.8441 |      6      |
|  `p2`   |    IP     |    1450    |    1452    |   13303   | 5.3529 |      9      |
|  `p2`   |    LS     |     86     |     88     |    841    | 69.571 |      9      |
|  `p3`   |    IP     |    5040    |    5042    |   44944   | 20.752 |     12      |
|  `p3`   |    LS     |    120     |    122     |   1067    | 138.68 |     12      |

[^IP]: `h_ignore_preconditions`
[^LS]: `h_levelsum`

To these specific problems, the plan lengths of these two heuristic searches are same. *A search with LS\** is more accurate[^1] than *that with LP*, so it expands less nodes and do less goal tests. It takes longer time, however, than the other, because of the cost of establishing a planning graph and the fact that the test data are not big enough to compensate that. So to these specific problems, I recommand *IP* as the best heuristic, it's fast and easy to implement, although it may use more resources. 

# Best Heuristic vs Best non-heuristic

| Problem | Search | Expansions | Goal Tests | NewNodes |  Time  | Plan Length |
| :-----: | :----: | :--------: | :--------: | :------: | :----: | :---------: |
|  `p1`   |  UCS   |     55     |     57     |   224    | 0.0457 |      6      |
|  `p1`   |   IP   |     41     |     43     |   170    | 0.0451 |      6      |
|  `p2`   |  UCS   |    4852    |    4854    |  44030   | 16.430 |      9      |
|  `p2`   |   IP   |    1450    |    1452    |  13303   | 5.3529 |      9      |
|  `p3`   |  UCS   |   12559    |   12561    |  111601  | 66.984 |     12      |
|  `p3`   |   IP   |    5040    |    5042    |  44944   | 20.752 |     12      |

[^UCS]: Uniform-Cost Search
[^IP]: A* Search with 'ignore_preconditions' heuristic

From above comparisons it's easy to see _A* Search with 'ignore preconditions' heuristic_  is better than *UCS* in general cases. Furthermore, the larger the problem is, the better performance _A* Search with 'ignore preconditions' heuristic_ gains.

[^1]: Because `GRAPHPLAN records mutexes to point out where the difficult interactions are` cited from *Artificial Intelligence A Mordern Approach*

