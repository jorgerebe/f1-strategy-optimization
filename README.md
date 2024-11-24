# F1 Race Strategy Optimization with Deep Reinforcement Learning

This project consists of a reinforcement learning agent that optimises race strategy decisions, improving average finish position by 3.2 places in 1000 simulated races compared to results
using real-world past strategies. In order to train the agent, an F1 race simulator has been built in Python. The agent learned by interacting in races with other drivers that used real
strategies used in past Grands Prix.

## Overview




## F1 Races Simulator 

The agent needs to interact with an environment in order to learn to optimise the race strategy for a driver. That environment is a discretised F1 races simulator, built with Python. In a race, there are be *n\_laps* laps and _T_ timesteps, numbered from 0 to *n_laps - 1*.  

### State

- Initial State [ _t = 0_ ]

  At the start of the simulation, the race begins, and the initial state t = 0 is the moment when the agent-controlled driver approaches the pit entry, where the first action must be taken.

- Intermediate States [ _t > 0 and t < n_laps - 1_ ]

  Intermediate states are from the second lap (_t = 1_) until the penultimate lap (_t = n_laps-2_), the last timestep where the driver can stop, as it would not make sense to pit in the last lap.

- Terminal State: [ _t = n_laps - 1 = T_ ]

  Simulator is in the terminal state when race is finished, the number of laps to go for every driver is 0.

### Actions

There are 4 possible actions that the agent can take in each timestep of the simulation:

- 0: No stop.
- 1: Box for a new set of soft tyres.
- 2: Box for a new set of medium tyres.
- 3: Box for a new set of hard tyres.

Therefore, _A_ is defined as the set of possible actions:

```math
$$A = \{0, 1, 2, 3\}$$
```


### Simulator Functionality

#### Time Simulation $[t \geq 0 \land t < n\\_laps - 1, a \in A]$

* ***Lap time  effect: Tyres and Fuel***

  Time of each driver is calculated using two variables: performance of current fitted set of tyres and mass effect of the remaining fuel.

  - Tyres effect
 
    Let $ci$ be the track where a driver is racing, $t$ a tyre set that a driver has fitted in her car, $ci.t\\_base$ the base time needed for a lap at the track $ci$, $n.t\\_min$ is defined as the effect on the lap time a new tyre set has:
    
  <p align="center">$$n.t\_min = ci.t\_base + n.compound.t\_add$$</p>

   Taken into account the degradation of the tyres, the effect of the tyres on the lap time is defined as follows:
   
  <p align="center">$$n.tyres\_effect = n.t\_min + n.compound.degradation \cdot (n.used\_laps)$$</p>
  
  - Fuel effect
  
  Let $f$ be the fuel of a car during a race. Consumed fuel is defined as:
  
  <p align="center">$$f.consumed\_fuel = (f.consumption\_per\_lap \cdot f.consumed\_laps)$$</p>

  Remaining fuel as:
  
  <p align="center">$$f.remaining\_fuel = f.initial\_mass - f.consumed\_fuel$$</p>

  Therefore, the effect on the lap time by the fuel mass effect is:
  
  <p align="center">$$f.fuel\_effect = f.remaining\\_fuel \cdot f.mass\_effect$$</p>

* ***Potential lap time***
  
  Let $p$ be a driver, its lap time, if she is in clean air, that is, her potential lap time $(plt)$ as:

```math
p.plt = n.tyres\_effect + f.fuel\_effect
```

* ***Time Simulation***

  Given state $S_t$ and action $A_t$, simulator advances to state $S_{t+1}$ by simulating the time needed for a event related to any of the drivers to happen. This event could be: **1)** get to the pit lane entry, **2)** get to the pit exit if the driver had pitted and **3)** get to the finish lane if she is on the last lap. If a driver $p$ has finished the racer $(p.ltg = 0)$, $p$ will have no more events, so the needed time for an event related to him to happen will be $\inf$.

  Let $p$ be a driver, the time needed for an event related to him to happen is defined as:

```math
time\_until\_event(p)=
    \begin{cases}
        \infty ,& \text{if } p.ltg = 0\\
        p.time\_until\_finish\_lane,              & \text{if } p.ltg = n\_laps\\
        p.time\_until\_pit\_exit,              & \text{if } p.in\_pits\\
        p.time\_until\_pit\_entry,              & \text{otherwise}
    \end{cases}
```

Therefore, the minimum time to simulate will be:

```math
time\_{to\_simulate} = \min_{p \in drivers} p.time\_until\_event(p)
```

* ***Percentage to advance***

  Once $plt$ for a driver $p$ and $time\\_to\\_simulate$ is known, supposing $p$ is in clean air, the percentage of lap that $p$ is going to advance in that time can be calculated. Let $percentage\\_to\\_advance$ be defined as:

```math
p.percentage\_to\_advance = \frac{time\_to\_simulate}{p.plt}
```

* ***Overtakes***

  If during the minimum time to simulate, a driver is expected to advance more than the driver she has in front, and is enough to overtake her, then she will overtake her with a certain probability $p\\_overtake$, depending on the track.

  Let $x$ a random number in the range $[0, 1)$, $c$ a track where race is happening, $p_1$ a driver, and $p_2$ a driver behind $p_1$, $time\\_until\\_next$ the needed time for $p_2$ to catch $p_1$, being $time\\_until\\_next \lt time\\_to\\_simulate$, then $p\_2.percentage\\_to\\_advance$ is redefined:

```math
p_2.percentage\_to\_advance =
    \begin{cases}
        \frac{time\_to\_simulate}{p_2.plt},              & \text{if } x < c.p\_overtake\\
        \frac{time\_until\_next - d\_no\_ov}{p_2.plt},              & \text{otherwise}
    \end{cases}
```

This means, with probability $c.p\\_overtake$, $p_2$ will overtake $p_1$, and with probability $1 - c.p\\_overtake$, $p_2$ will stay $d\\_no\\_ov$ seconds behind $p_1$.

#### Variability

Every moment in an F1 race is different, so tyres performance and degradation will be different for each tyre set of the same compound.

Every driver that is not being controlled will use a predefined strategy estimated from real races, but will not always be the same, but there will be variability in the lap number for each pitstop. Furthermore, each predefined strategy will have a probability of being assigned to a driver. The start tyre of the driver being controlled will come from a predefined strategy, with the same probability as for the rest of the drivers.

## Experimental Setup

### Simulator Configuration


### Algorithms

Three algorithms have been used for the experiments:

1. DQN
2. QR-DQN
3. A2C

### Reward Functions

The reward function is a critical element in a reinforcement learning system. Is the only signal the agent can use to know how well it is performing, so it is critical to design a good reward function and consider a couple of them and see what is the one with which better results are achieved.

#### Common elements to all the reward functions

In order to comply with the simulator restrictions, a negative reward will be given to the agent every time it takes a decision that is not in conformity with any of them:

- If at the end of the race the driver has not used two different tyre compounds, then it will receive a negative reward of -1, apart from being disqualified from the race.
- If the agent stops more than the maximum number of allowed stops, it means that it is trying to stop when no more tyres are available, which will result in an additional reward of -1 every time it pits when the limit has been surpassed.

#### R1 - Positions gained per lap

Reward function R1 gives a reward based in the number of positions gained (or lost) by the agent from time-step \(t-1\) until time-step \(t\), that is, per lap.

```math
R_1 = position_{t-1} - position_t
```

Experiments using this reward function will be with races where driver controlled by agent will always be starting last.

#### R2 - Positions gained per lap, normalized by number of laps to go

Reward function R2 is quite similar to R1, but in this case, changes of position are more important when race is closer to end.

```math
R_2 = (position_{t-1} - position_t) \cdot \frac{(t+1)}{\textnormal{n\_laps - 1}}
```
Experiments using this reward function will be with races where driver controlled by agent will always be starting last.

#### R3 - Reward Based on Final Position

Reward function R3 will give a reward to the agent only when the race is finished, based on its finishing position. This way, agent can be trained in more realistic conditions (grid with random order).

From the first position to the last, a reward has been assigned to each position, which will be given to the agent at the end of the race based on its finishing position. The function $r3\\_aux(p)$ is defined as a function that takes a position as input and returns the associated reward, as shown in the following table:

<table align=center>
  <tr>
    <th style="background-color:#ECF4FF;">Position</th>
    <th style="background-color:#FFFFC7;">Reward</th>
    <th style="background-color:#ECF4FF;">Position</th>
    <th style="background-color:#FFFFC7;">Reward</th>
    <th style="background-color:#ECF4FF;">Position</th>
    <th style="background-color:#FFFFC7;">Reward</th>
    <th style="background-color:#ECF4FF;">Position</th>
    <th style="background-color:#FFFFC7;">Reward</th>
  </tr>
  <tr>
    <td>1</td><td>15</td><td>2</td><td>13.5</td><td>3</td><td>12.25</td><td>4</td><td>11</td>
  </tr>
  <tr>
    <td>5</td><td>9.75</td><td>6</td><td>8.75</td><td>7</td><td>8.0</td><td>8</td><td>7.25</td>
  </tr>
  <tr>
    <td>9</td><td>6.5</td><td>10</td><td>5.75</td><td>11</td><td>5.0</td><td>12</td><td>4.25</td>
  </tr>
  <tr>
    <td>13</td><td>3.75</td><td>14</td><td>3.25</td><td>15</td><td>1.75</td><td>16</td><td>1.25</td>
  </tr>
  <tr>
    <td>17</td><td>0.75</td><td>18</td><td>0.5</td><td>19</td><td>0.25</td><td>20</td><td>0</td>
  </tr>
</table>

```math
R3 = \begin{cases} r3\_aux(position), & \text{if } t = T \\ 0 & \text{otherwise} \end{cases}
```
Experiments using this reward function will be with races where driver controlled by agent will always be starting last, and also with the agent starting in a random position. This means that the number of experiments for this reward function will be the double.

## Results

## Evaluation and Best Model Selection

Each model was evaluated across 1,000 unique race simulations. These races had different configurations, including randomized starting grids and varied strategies for the competing drivers. To ensure a fair comparison, each model evaluation used the same initial conditions for all the 1,000 races. This approach allowed consistent starting conditions across different algorithms and reward functions, enabling a direct comparison of performance.

<table border="1" cellspacing="0" cellpadding="5" align=center>
  <tr>
    <th rowspan="3"></th>
    <th colspan="8">Reward Function</th>
  </tr>
  <tr>
    <th colspan="2">R1</th>
    <th colspan="2">R2</th>
    <th colspan="4">R3</th>
  </tr>
  <tr>
    <th colspan="8">Grid order during training</th>
  </tr>
  <tr>
    <td>Algorithm</td>
    <td colspan="7">Fixed, driver controlled by agent always starts last</td>
    <td>Random</td>
  </tr>
  <tr>
    <td><b>DQN</b></td>
    <td colspan="2">11.267 ± 5.8142</td>
    <td colspan="2">11.904 ± 4.4028</td>
    <td colspan="3">11.645 ± 5.6116</td>
    <td>11.267 ± 4.8727</td>
  </tr>
  <tr>
    <td><b>QR-DQN</b></td>
    <td colspan="2">10.459 ± 6.3136</td>
    <td colspan="2">10.836 ± 5.9980</td>
    <td colspan="3">11.939 ± 5.3223</td>
    <td>13.091 ± 6.0941</td>
  </tr>
  <tr>
    <td><b>A2C</b></td>
    <td colspan="2"><b>9.802 ± 6.8928</b></td>
    <td colspan="2"><b>10.069 ± 7.1327</b></td>
    <td colspan="3"><b>7.684 ± 5.5076</b></td>
    <td><b>7.208 ± 5.2351</b></td>
  </tr>
</table>




## Conclusions and Future Work

### Conclusions

### Future Work

