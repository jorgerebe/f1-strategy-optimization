# F1 Race Strategy Optimization with Deep Reinforcement Learning

This project consists of a reinforcement learning agent that optimises race strategy decisions, improving average finish position by 3.2 places in 1000 simulated races compared to results
using real-world past strategies. In order to train the agent, a F1 race simulator has been built in Python. The agent learned by interacting in races with other drivers that used real
strategies used in past Grand Prixes.

## Overview

## Simulator Configuration

## Experimental Setup

### Algorithms

Three algorithms have been used for the experiments:

1. DQN
2. QR-DQN
3. A2C

### Reward Functions

The reward function is a critical element in a reinforcement learning system. Is the only signal that the agent can use to know how well it is performing, so it is critical to design a good reward function and consider a couple of them and see what is the one with which better results are achieved.

#### Common elements to all the reward functions

In order to comply with the simulator restrictions, a negative reward will be given to the agent every time it takes a decision that is not in conformity with any of them:

- If at the end of the race the driver has not used two different tyre compounds, then it will receive a negative reward of -1, appart from being disqualified from the race.
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

From the first position to the last, a reward has been assigned to each position, which will be given to the agent at the end of the race based on its finishing position. The function r3_aux(p) is defined as a function that takes a position as input and returns the associated reward, as shown in the following table:

<table>
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

Each model was evaluated across 1,000 unique race simulations. These races had different configurations, including randomized starting grids and varied strategies for the competing drivers. Ro ensure a fair comparison, each model evaluation used the same set of 1,000 races. This approach allowed consistent starting conditions across different algorithms and reward functions, enabling a direct comparison of performance.

<table border="1" cellspacing="0" cellpadding="5">
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

