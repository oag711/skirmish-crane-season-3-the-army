"""Season 3 Crane Reach army agent.

Footmen hold the frontline, archers attack from range,
and cavalry move quickly to attack vulnerable enemies.
"""

from sandbox.crane import action, me, paths, tile, units, visible
from sandbox.observation_types import AxialPosition, SkirmishAction, SkirmishObservation


class Agent:
    """Uses different combat strategies for each unit type."""

    def reset(self, seed, observation) -> None:
        # This agent makes decisions from the current observation.
        # It does not need to save anything between turns.
        pass

    def act(self, observation: SkirmishObservation) -> SkirmishAction:
        # Find the enemies and allies this unit can currently see.
        enemies = visible.enemies(observation)
        allies = visible.allies(observation)

        # Read this unit's type and current position.
        unit_type = me.unit_type(observation)
        here = me.position(observation)

        # If no enemies are visible, move toward the center.
        if not enemies:
            center = tile.at_center(observation)
            path_id = self._step_toward(
                observation, center, allies, unit_type
            )

            if path_id == 0:
                return action.stay()

            return action.move(path_id)

        # Choose a target according to this unit's role.
        target = self._choose_target(here, enemies, unit_type)

        # Find the best legal route toward the target.
        path_id = self._step_toward(
            observation, target["position"], allies, unit_type
        )

        # Name the target so the game tries to attack it after moving.
        if path_id == 0:
            return action.stay(target["unit_id"], observation)

        return action.move(
            path_id, target["unit_id"], observation
        )

    def _choose_target(self, here, enemies, unit_type):
        """Choose an enemy based on distance, health, and role."""

        best_target = enemies[0]
        best_score = 100000

        for enemy in enemies:
            distance = tile.distance(here, enemy["position"])

            # Nearby enemies are usually easier to attack.
            score = distance * 5

            # Prefer enemies with less health so the army can defeat them.
            score = score + enemy["hit_points"] * 1.5

            # Give extra priority to enemies that can be defeated soon.
            if enemy["hit_points"] <= 3:
                score = score - 8

            # Cavalry try to pressure enemy archers.
            if unit_type == "cavalry":
                if enemy["type"] == "archer":
                    score = score - 8

            # Archers prefer vulnerable enemy units.
            if unit_type == "archer":
                if enemy["type"] == "archer":
                    score = score - 4

            # Footmen help deal with nearby frontline threats.
            if unit_type == "footman":
                if enemy["type"] == "cavalry":
                    score = score - 5

            if score < best_score:
                best_score = score
                best_target = enemy

        return best_target

    def _step_toward(
        self,
        observation: SkirmishObservation,
        goal: AxialPosition,
        allies,
        unit_type: str
    ) -> int:
        """Choose the legal path that best supports this unit's role."""

        here = me.position(observation)
        enemies = visible.enemies(observation)

        # Start with staying in place as a valid choice.
        best_path = 0
        best_score = -100000

        # Consider every legal path, including multi-step paths.
        for path_id in action.legal_paths(observation):
            end = tile.at_path_end(here, path_id)
            distance = tile.distance(end, goal)

            # Moving closer is useful for footmen and cavalry.
            score = -distance * 5

            # Count the directions in this path.
            directions = paths.decode(path_id)

            # Small preference for shorter routes when scores are similar.
            score = score - len(directions) * 0.1

            # Footmen benefit from standing beside allied footmen.
            if unit_type == "footman":
                for ally in allies:
                    if ally["type"] == "footman":
                        ally_distance = tile.distance(
                            end, ally["position"]
                        )

                        if ally_distance == 1:
                            score = score + 4

            # Cavalry benefit from moving at least three hexes
            # before their attack to activate the charge bonus.
            if unit_type == "cavalry":
                if tile.distance(here, end) >= 3:
                    score = score + 8

                # Cavalry should favor attacking archers.
                for enemy in enemies:
                    if enemy["type"] == "archer":
                        enemy_distance = tile.distance(
                            end, enemy["position"]
                        )

                        if enemy_distance == 1:
                            score = score + 5

            # Archers want to remain within shooting range.
            if unit_type == "archer":
                attack_range = units.STATS["archer"].attack_range

                for enemy in enemies:
                    enemy_distance = tile.distance(
                        end, enemy["position"]
                    )

                    # Prefer positions from which the archer can shoot.
                    if enemy_distance <= attack_range:
                        score = score + 12

                        # Prefer some distance from nearby enemies.
                        if enemy_distance >= 3:
                            score = score + 3

                    # Avoid ending adjacent to melee enemies.
                    if enemy["type"] == "footman":
                        if enemy_distance <= 1:
                            score = score - 18

                    if enemy["type"] == "cavalry":
                        if enemy_distance <= 2:
                            score = score - 22

            # Prefer paths that finish within attack range of an enemy.
            for enemy in enemies:
                enemy_distance = tile.distance(
                    end, enemy["position"]
                )

                if enemy_distance <= units.STATS[unit_type].attack_range:
                    score = score + 10

            # Prefer this route if its score is better.
            if score > best_score:
                best_score = score
                best_path = path_id

        return best_path


    # Optional: a reinforcement-learning hook called after every step with that step's
    # transition. Its time counts against the timing and episode budget. The order argument is
    # what act returned. It is named order so it does not shadow the action helpers.
    #
    # def learn(self, observation, order: SkirmishAction, reward: float, terminated: bool) -> None:
    #     ...

    # Optional: messaging. Season settings enable it from Season 3 onward. When enabled, chat runs
    # after a unit chooses its order and receives messages that arrived since its previous
    # activation. Return each message with a recipient and text. Use None to broadcast to both
    # sides, or a player id such as "player_2", not a unit id, to send directly to one ally. The
    # rosters in the observation map each player to its unit. By default, text is limited to 200
    # characters.
    # A direct message reaches its allied unit at its next activation, after that unit chooses its
    # own order. Every message is recorded and shown in replays, so nothing you send is ever secret.
    # Return nothing to stay silent.
    #
    # def chat(self, inbox: list[dict]) -> list[dict] | None:
    #     ...