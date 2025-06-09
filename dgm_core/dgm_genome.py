# dgm_core/dgm_genome.py
# Represents the genetic makeup of a Darwin Gödel Machine instance.

import json
from dataclasses import dataclass, field, asdict

@dataclass
class Genome:
    """
    Defines the evolvable traits of a DGM instance.
    This structure is serialized to dgm_genome.json.
    """
    # Strategy 1: Resource-Aware Model-Switching Policy
    solver_policy: dict = field(default_factory=lambda: {
        'easy_model': 'gemma:2b',
        'hard_model': 'llama3:8b',
        'complexity_threshold': 0.7
    })

    # Strategy 2: Evolvable Mutator Model
    # This gene determines the cognitive engine used for self-mutation.
    mutator_model: str = 'llama3:8b'
    
    fitness: float = 0.0
    # Meta-fitness tracking for the mutator model lineage
    generation: int = 0
    parent_id: int = 0
    genome_id: int = 0

    def to_json(self, filepath: str):
        """Serializes the genome to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=4)

    @classmethod
    def from_json(cls, filepath: str):
        """Deserializes the genome from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            # Handle legacy genomes that may not have new fields
            if 'generation' not in data:
                data['generation'] = 0
            if 'parent_id' not in data:
                data['parent_id'] = 0
            if 'genome_id' not in data:
                data['genome_id'] = data.get('generation', 0)
            if 'mutator_model' not in data:
                data['mutator_model'] = 'llama3:8b' # Default for older genomes
            return cls(**data)
        except FileNotFoundError:
            # Return a default genome if the file doesn't exist
            genome = cls()
            genome.genome_id = 1 # Start with ID 1
            return genome
