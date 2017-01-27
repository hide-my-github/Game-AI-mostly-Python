1. 	New forces: 
	1. Confuse: Depending on behavior0, there is a % chance for the flock to completely change directions.
	2. Flash: If the largest force of the flock is under a certain amount, that amount will be multiplied by behavior1 * 20. Thus making that highest influencing vector much stronger and will result in the flock being faster.
	3. Follow: The amount of mouse pointer influence is directly proportional to behavior2.

2.	The two new fitness functions that we implemented attempted to pick winners based on things other than food. The first
	picked winners based on the level of forces that were acting upon the boids, i.e. picking boids that moved faster and/or
	more dramatically than the other flocks. This one worked ok, although because the flocks are automatically speed controlled
	it meant that the child flocks would hit an upward limit on the forces being acted upon them. The second function picked
	winners based on the length of their wings, and was more of an aesthetic fitness function than a behavioral one. It made
	for very pretty, long-winged boids, although there really wasn't a behavioral change (which was expected with this).

3. 	Evolving flocks: 