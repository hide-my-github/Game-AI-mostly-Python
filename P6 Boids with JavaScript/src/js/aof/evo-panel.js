/**
 * @author Kate Compton
 *
 * Evolutionary algorithm functions
 */

function EvoPanel() {
	var panel = this;

	this.winnerSlots = [];

	// Create winner slots
	for (var i = 0; i < app.winnerSlots; i++) {
		this.winnerSlots[i] = {
			div : $("<div/>", {
				class : "subpanel winner-slot",
			}).appendTo($("#winner-slots"))
		};
	}

	$.each(this.winnerSlots, function(index, slot) {
		slot.div.droppable({
			activeClass : "section-active",
			hoverClass : "section-hover",
			drop : function(event, ui) {
				addToWinnerSlot(index, panel.draggedSlot);
				panel.draggedSlot = undefined;
			}
		});
	});

	function addToWinnerSlot(index, fromSlot) {
		console.log(index + " ", fromSlot);
		panel.winnerSlots[index].fromSlot = fromSlot;
		panel.winnerSlots[index].individual = fromSlot.individual;
		panel.winnerSlots[index].div.css({
			backgroundImage : "url(" + fromSlot.dataURL + ")"
		});

	};

	app.showDNA = true;
	$("#toggle-dna").click(function() {
		app.showDNA = !app.showDNA;
		console.log(app.showDNA);
		if (app.showDNA)
			$(".overlay-content").show();
		else
			$(".overlay-content").hide();
	});
	$("#toggle-forces").click(function() {
		app.showForces = !app.showForces;

	});

	$("#reroll").click(function() {
		app.population.reroll();
		updatePopulationUI();
	});

	$("#mut-chance").slider({
		value : app.mutationChance,
		min : 0,
		max : 1,
		step : .02,
		slide : function(event, ui) {
			console.log("mutationChance: " + ui.value);
			app.mutationChance = ui.value;
		}
	});

	$("#mut-amt").slider({
		value : app.mutationAmt,
		min : 0,
		max : .2,
		step : .01,
		slide : function(event, ui) {
			console.log("mutationAmt: " + ui.value);
			app.mutationAmt = ui.value;
		}
	});

	$("#nextgen").click(function() {
		var evolutionType = $("input[name=evomode]:checked").val();
		console.log(evolutionType);

		var nextGeneration = [];

		var allParents = app.population.individuals;

		switch(evolutionType) {
		case("random") :
			for (var i = 0; i < app.popCount; i++) {
				var randomDNA = app.population.createDNA();
				nextGeneration[i] = app.population.dnaToIndividual(randomDNA);
			}
			break;
		case("mutateAll") :
			console.log("Mutate all parents into new children");
			for (var i = 0; i < app.popCount; i++) {
				var childDNA = allParents[i].dna.createMutant(app.mutationAmt, app.mutationChance);
				nextGeneration[i] = app.population.dnaToIndividual(childDNA);
			}
			break;

		case("mutateWinners") :
			console.log("Mutate all winners into new children");
			// Get all the winners
			var winners = app.evoPanel.winnerSlots.map(function(slot) {
				return slot.individual;
			}).filter(function(winner) {
				return winner !== undefined;
			});

			// Create children from the parents.  At least one chid from each parent,
			//  but the rest can select a random parent from the winner list
			for (var i = 0; i < app.popCount; i++) {
				var parent = winners[i];

				// pick a random parent for extra children
				if (i >= winners.length) {
					parent = winners[Math.floor(winners.length * Math.random())];
				}
				var childDNA = parent.dna.createMutant(app.mutationAmt, app.mutationChance);
				nextGeneration[i] = app.population.dnaToIndividual(childDNA);

			}

			break;
		case("breedWinners") :
			var winners = app.evoPanel.winnerSlots.map(function(slot) {
				return slot.individual;
			}).filter(function(winner) {
				return winner !== undefined;
			});

			// Pick parents randomly from winners, and crossover their DNA to create a new child
			for (var i = 0; i < app.popCount; i++) {
				var rawDNA0 = winners[Math.floor(winners.length * Math.random())].dna.values;
				var rawDNA1 = winners[Math.floor(winners.length * Math.random())].dna.values;

				/*
				 * TODO: Replace this with real crossover
				 * The raw DNA is just an array of floats [0,1]
				 * Use that to fill in the childDNA with the right values
				 *
				 * DONE
				 */
				var childDNA0 = app.population.createDNA();
				var childDNA1 = app.population.createDNA();
				var crossPlace = Math.floor(rawDNA0.length * Math.random());
				for (var j = 0; j < childDNA0.values.length; j++) {
					if(j <= crossPlace){
						childDNA0.values[j] = rawDNA0[j];
					} else{
						childDNA0.values[j] = rawDNA1[j];
					}
				}
				for (var j = 0; j < childDNA1.values.length; j++) {
					if(j <= crossPlace){
						childDNA1.values[j] = rawDNA1[j];
					} else{
						childDNA1.values[j] = rawDNA0[j];
					}
				}
				
				nextGeneration[i] = app.population.dnaToIndividual(childDNA0);
				nextGeneration[i+1] = app.population.dnaToIndividual(childDNA1);
			
			}

			break;

		/*
		 * Create two new kinds new breeding behavior
		 * Combine mutation with crossover?
		 * The aesthetic DNA is at indicies 0-9, and the behavior DNA is at indicies 10-19
		 * Can you use that information somehow?
		 */
		case("custom1") :
			/*
			 * Creates two children whose behavior is crossed between the parents but is the
			 * same for both, but who have the exact aesthetic of either parent 0 or parent 1 
			 * (child 0 looks like parent 0, and child 1 looks like parent 1)
			 */
		
			var winners = app.evoPanel.winnerSlots.map(function(slot) {
				return slot.individual;
			}).filter(function(winner) {
				return winner !== undefined;
			});

			for (var i = 0; i < app.popCount; i++) {
				var rawDNA0 = winners[Math.floor(winners.length * Math.random())].dna.values;
				var rawDNA1 = winners[Math.floor(winners.length * Math.random())].dna.values;

				var childDNA0 = app.population.createDNA();
				var childDNA1 = app.population.createDNA();
				var crossPlace = Math.floor(10 * Math.random()) + 10;
				for (var j = 0; j < childDNA0.values.length; j++) {
					if(j < 10){
						childDNA0.values[j] = rawDNA0[j];
					}
					else if(j <= crossPlace){
						childDNA0.values[j] = rawDNA0[j];
					} else{
						childDNA0.values[j] = rawDNA1[j];
					}
				}
				for (var j = 0; j < childDNA1.values.length; j++) {
					if(j < 10){
						childDNA1.values[j] = rawDNA1[j];
					}
					else if(j <= crossPlace){
						childDNA1.values[j] = rawDNA0[j];
					} else{
						childDNA1.values[j] = rawDNA1[j];
					}
				}
				nextGeneration[i] = app.population.dnaToIndividual(childDNA0);
				nextGeneration[i+1] = app.population.dnaToIndividual(childDNA1);
			}
			break;
			
		case("custom2") :
			/*
			 * Creates two children whose aesthetic is crossed between the parents, but
			 * whose behavior is completely random
			 */
		
			var winners = app.evoPanel.winnerSlots.map(function(slot) {
				return slot.individual;
			}).filter(function(winner) {
				return winner !== undefined;
			});

			for (var i = 0; i < app.popCount; i++) {
				var rawDNA0 = winners[Math.floor(winners.length * Math.random())].dna.values;
				var rawDNA1 = winners[Math.floor(winners.length * Math.random())].dna.values;

				var childDNA0 = app.population.createDNA();
				var childDNA1 = app.population.createDNA();
				var crossPlace = Math.floor(10 * Math.random());
				for (var j = 0; j < childDNA0.values.length; j++) {
					if(j >= 10){
						childDNA0.values[j] = Math.random();
					}
					else if(j <= crossPlace){
						childDNA0.values[j] = rawDNA0[j];
					} else{
						childDNA0.values[j] = rawDNA1[j];
					}
				}
				for (var j = 0; j < childDNA1.values.length; j++) {
					if(j >= 10){
						childDNA1.values[j] = Math.random();
					}
					else if(j <= crossPlace){
						childDNA1.values[j] = rawDNA1[j];
					} else{
						childDNA1.values[j] = rawDNA0[j];
					}
				}
				nextGeneration[i] = app.population.dnaToIndividual(childDNA0);
				nextGeneration[i+1] = app.population.dnaToIndividual(childDNA1);
			}
			break;
		};

		app.population.individuals = nextGeneration;
		app.evoPanel.clearWinners();
		updatePopulationUI();
	});

	$("#set-winners").click(function() {
		
		// default Fitness: food
		var sorted = app.population.individuals.sort(function(a, b) {
			return b.food - a.food;
		});
		
		// alt Fitness 1: forces
		/* 
		 *  var sorted = app.population.individuals.sort(function(a, b) {
		 *		return b.forces - a.forces;
		 * });
		 */
		 
		// alt Fitness 2: wing length
		/* 
		 * var sorted = app.population.individuals.sort(function(a, b) {
		 *		return b.wingLength - a.wingLength;
		 * });
		 */
		 
		for (var i = 0; i < 3; i++) {
			app.evoPanel.addToWinners(sorted[i], i);
		}
	});

}

EvoPanel.prototype.clearWinners = function() {
	for (var i = 0; i < this.winnerSlots.length; i++) {
		this.winnerSlots[i].div.css({
			backgroundImage : "none"
		});
		this.winnerSlots[i].individual = undefined;
	}
};

EvoPanel.prototype.addToWinners = function(individual, index) {
	this.winnerSlots[index].div.css({
		backgroundImage : "url(" + individual.thumbnailURL + ")",
		backgroundSize : "100%"
	});
	this.winnerSlots[index].individual = individual;
};

