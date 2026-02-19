# Life as Turing Complete

This notebook demonstrates implementation for Module 1 of my Modelling complex system's course.
I embarked on implementing a from scratch pipeline that tries to prove Conways Game of Life (CGoL) as Turing Complete

Name: Darsh SA

Reg. No: MS22068

## Turing Completeness in Game of Life

A system is **Turing complete** if it can simulate any Turing machine given enough space/time.

Thus we formalise the requirements to prove CGoL as Turing complete as:

1. Life supports signal transmission.
2. Life supports universal Boolean logic.
3. Life supports memory (feedback, latch).

Conway's Game of Life is known to be Turing complete in theory. This notebook shows how this implementation builds those ingredients concretely.

---

## 1. Basic Rules of Conway's Game of Life

Conway's Life uses `B3/S23`:
- Birth: dead cell with exactly 3 neighbors becomes alive.
- Survival: live cell survives with 2 or 3 neighbors.

![rule.png](docs/demo_outputs/rule.png)

Thus using the above ruleset CGoL gives birth to various different patterns
ref: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Pattern_taxonomy

one of the most common pattern "The Glider" is generated below

**Output**
![glider_t0](docs/demo_outputs/glider_t0.png)
Animation: [glider_motion.mp4](docs/demo_outputs/glider_motion.mp4)

## 2. Components and Patterns in This Project

To prove CGoL is Turing Complete we will use some of the following patterns as building blocks of our system:
- `glider`
- `gun`
- `eater`
- `reflector`

From these patterns (or hereby called atomic componenents) we can build all the componenets required by our system to prove its turing complete

**Output**

| Component | Snapshot | Animation |
| --- | --- | --- |
| `glider` | ![atomic_glider_grid_snapshot.png](docs/demo_outputs/atomic_glider_grid_snapshot.png) | ![atomic_glider_grid_motion.gif](docs/demo_outputs/atomic_glider_grid_motion.gif) |
| `gun` | ![atomic_gun_grid_snapshot.png](docs/demo_outputs/atomic_gun_grid_snapshot.png) | ![atomic_gun_grid_motion.gif](docs/demo_outputs/atomic_gun_grid_motion.gif) |
| `eater` | ![atomic_eater_grid_snapshot.png](docs/demo_outputs/atomic_eater_grid_snapshot.png) | ![atomic_eater_grid_motion.gif](docs/demo_outputs/atomic_eater_grid_motion.gif) |
| `reflector` | ![atomic_reflector_grid_snapshot.png](docs/demo_outputs/atomic_reflector_grid_snapshot.png) | ![atomic_reflector_grid_motion.gif](docs/demo_outputs/atomic_reflector_grid_motion.gif) |

---

## 3. Proving Turing Completeness

Now that we have our building blocks setup we have start wit ticking off what makes CGoL Turing complete and implement each requirement

### A. Signal Transmition

We implement signal ticks by using the `Glider` and then a stream of gliders represent a signal. As we saw earlier a stream of gliders can be created with something called Glider guns, here we have used a [Gospers Glider Gun](https://conwaylife.com/wiki/Gosper_glider_gun)

Now for propogation, we want our signal to redirect in any direction we want. For this we use the [Reflector](https://conwaylife.com/wiki/Reflector) components. Theres various types of reflectors that have different reflection angle build into them.

Thus first criteria is now complete!!

**Output**
![reflector_gun_setup](docs/demo_outputs/reflector_gun_setup.png)
Animation: [reflector_gun_motion.mp4](docs/demo_outputs/reflector_gun_motion.mp4)

### B. Boolean Logic

We represent boolean logic in computation by `Logic Gates`. The basic logic gates are `NOT`, `AND` and `OR`.
From these three basic gates all combination of boolean operation and different kinds of gates can be made.

##### NOT Gate
This is the most simplest one, we have an input stream, and the gate consists of another `gun` that cancels out the input stream

##### AND Gate
This conists of two inputs, we can employ a similar implementation to NOT gate here and if only both inputs are on we get an output

##### OR Gate
Here we use the AND gate but add another `gun` and an `eater` right at the end of the second input. Thus when no input is present the second `gun` inside the component is blocked and if even one input is present the second `gun` gives out an output



*All the combinations of inputs can be found in the output directory as video files for review

**Output**

##### NOT Gate Output
![not_gate_setup](docs/demo_outputs/not_gate_demo_setup.png)
Animation: [not_gate_motion.mp4](docs/demo_outputs/not_gate_demo_motion.mp4)

##### AND Gate Output
![and_gate_setup](docs/demo_outputs/and_gate_demo_setup.png)
Animation: [and_gate_motion.mp4](docs/demo_outputs/and_gate_demo_motion.mp4)

##### OR Gate Output
![or_gate_setup](docs/demo_outputs/or_gate_demo_setup.png)
Animation: [or_gate_motion.mp4](docs/demo_outputs/or_gate_demo_motion.mp4)

Thus now we satisfy the second condiiton!!

### C. Memory

We can use a simple SR-Latch here to satisfy the requirement.

Due to time constraints i wasnt able to implement the memory latch so heres a reference from one of the guides i was following:

![latch.gif](docs/demo_outputs/latch.gif)

---

With this we prove that CGoL is Turing Complete!!!

## 5) Circuit Composition Demo: AND -> NOT

Port-aligned composition with gate input enabling.

**Output**
![and_to_not_setup](docs/demo_outputs/and_to_not_setup.png)
Animation: [and_to_not_motion.mp4](docs/demo_outputs/and_to_not_motion.mp4)

## 4. Conclusion
The Repository represents a from scratch pipeline for proving life as turing complete while also building a starter pipeline to build a turing machine later on. In the current state the repository is just implemnented as a proof of concept though i tried making it as practical as possible.

In future I would like to expand the implementation of the pipeline and working on building some circuits using CGoL

#### References:
Main Motivation and Reference: https://www.alanzucconi.com/2020/10/13/conways-game-of-life/

https://bespoyasov.me/blog/binary-adder-in-the-game-of-life-2/
https://github.com/bespoyasov/binary-full-adder-in-the-game-of-life

Source for RLEs: 
- https://conwaylife.com/wiki/Main_Page
- https://golly.sourceforge.io/
- https://copy.sh/life/?pattern=snark

---

All the eye-candy are stored in tests/output folder, feel free to look around!

peace <3
