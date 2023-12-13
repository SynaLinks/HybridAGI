import asyncio
from .evaluation_reasoner import EvaluationReasoner

class RankedActionReasoner(EvaluationReasoner):
    """LLM reasoner that use ranked inferences to perform better"""
    
    def ranked_tool_input_prediction(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            ranked_inferences: int):
        """Method to predict the tool_name's input parameters
        using quality evaluation and ranked inferences"""
        predictions = []
        scores = []

        def get_prediction():
            prediction = self.predict_tool_input(
                purpose,
                tool_name,
                tool_prompt)
            predictions.append(prediction)

        for _ in range(ranked_inferences):
            get_prediction()

        def get_score(prediction):
            prediction = self.perform_evaluation(
                purpose,
                tool_name,
                tool_prompt,
                prediction)
            scores.append(prediction)

        for prediction in range(predictions):
            get_score(prediction)

        prediction_score_pairs = zip(predictions, scores)
        sorted_predictions = sorted(
            prediction_score_pairs,
            key=lambda x: x[1],
            reverse=True)
        best_prediction, _ = sorted_predictions[0]
        return best_prediction

    async def async_ranked_tool_input_prediction(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            ranked_inferences: int):
        """Method to asynchronously predict the tool_name's input parameters
        using quality evaluation and ranked inferences 
        """
        predictions = []
        scores = []
        
        async def get_prediction():
            prediction = await self.async_predict_tool_input(
                purpose,
                tool_name,
                tool_prompt,
            )
            predictions.append(prediction)
        
        tasks = [get_prediction() for _ in range(ranked_inferences)]
        await asyncio.gather(*tasks)

        async def get_score(prediction):
            prediction = await self.async_perform_evaluation(
                purpose,
                tool_name,
                tool_prompt,
                prediction,
            )
            scores.append(prediction)
        
        tasks = [get_score(predictions[i]) for i in range(len(predictions))]
        await asyncio.gather(*tasks)

        prediction_score_pairs = zip(predictions, scores)
        sorted_predictions = sorted(
            prediction_score_pairs,
            key=lambda x: x[1],
            reverse=True)
        best_prediction, _ = sorted_predictions[0]
        return best_prediction

    def perform_action(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            disable_inference: bool = False,
            ranked_inferences: int = 1,
        ) -> str:
        """Method to perform an action"""
        if self.pre_action_callback is not None:
            self.pre_action_callback(
                purpose,
                tool_name,
                tool_prompt,
            )
        if disable_inference:
            tool_input = tool_prompt
        else:
            if ranked_inferences == 0:
                tool_input = tool_prompt
            elif ranked_inferences == 1:
                tool_input = self.predict_tool_input(
                    purpose = purpose,
                    tool_name = tool_name,
                    tool_prompt = tool_prompt,
                )
            elif ranked_inferences > 1:
                tool_input = self.ranked_tool_input_prediction(
                    purpose = purpose,
                    tool_name = tool_name,
                    tool_prompt = tool_prompt,
                    ranked_inferences = ranked_inferences,
                )
            else:
                raise ValueError("Ranked inferences parameter should be positive")
        self.validate_tool(tool_name)
        tool_observation = self.execute_tool(tool_name, tool_input)
        action_description = self.get_action_description(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        self.trace_memory.commit_action(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        if self.post_action_callback is not None:
            self.post_action_callback(
                purpose,
                tool_name,
                tool_input,
                tool_observation,
            )
        return action_description

    async def async_perform_action(
            self,
            purpose: str,
            tool_name:str,
            tool_prompt: str,
            disable_inference: bool = False,
            ranked_inferences: int = 1,
        ) -> str:
        """Method to perform an action"""
        if self.pre_action_callback is not None:
            asyncio.create_task(
                self.pre_action_callback(
                    purpose,
                    tool_name,
                    tool_prompt,
                )
            )
        if disable_inference:
            tool_input = tool_prompt
        else:
            if ranked_inferences == 0:
                tool_input = tool_prompt
            elif ranked_inferences == 1:
                tool_input = await self.async_predict_tool_input(
                    purpose = purpose,
                    tool_name = tool_name,
                    tool_prompt = tool_prompt,
                )
            elif ranked_inferences > 1:
                tool_input = await self.async_ranked_tool_input_prediction(
                    purpose = purpose,
                    tool_name = tool_name,
                    tool_prompt = tool_prompt,
                    ranked_inferences = ranked_inferences,
                )
            else:
                raise ValueError("Ranked inferences parameter should be positive")
        self.validate_tool(tool_name)
        tool_observation = self.execute_tool(tool_name, tool_input)
        action_description = self.get_action_description(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        self.trace_memory.commit_action(
            purpose = purpose,
            tool_name = tool_name,
            tool_input = tool_input,
            tool_observation = tool_observation,
        )
        if self.post_action_callback is not None:
            asyncio.create_task(
                self.post_action_callback(
                    purpose,
                    tool_name,
                    tool_input,
                    tool_observation,
                )
            )
        return action_description