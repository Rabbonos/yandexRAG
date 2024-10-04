from typing import List
import asyncio

class CharacterLevelTextSplitter:
    def __init__(self, max_length: int = 6000, overlap: int = 300):
        """
        Initializes the character-level text splitter.

        Parameters:
            max_length (int): Maximum length of a split segment.
            overlap (int): Number of overlapping characters between segments.
        """
        self.max_length = max_length
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits the text into segments based on specified character length criteria and overlap.

        Parameters:
            text (str): The text to be split.

        Returns:
            List[str]: A list of text segments.
        """
        segments = []
        current_index = 0
        text_length = len(text)
        end_index=0
        while end_index < text_length:
            # Calculate the end index for the segment
            end_index = min(current_index + self.max_length, text_length)
            segment = text[current_index:end_index]

            segments.append(segment)

            # Move to the next segment start index, including overlap
            current_index = end_index - self.overlap

            # Prevent moving backward if overlap exceeds max_length
            if current_index < 0:
                break
        
        return segments

# # Example usage
# if __name__ == "__main__":
#     text = """....."""

#     splitter = CharacterLevelTextSplitter()
#     segments = await splitter.split_text(text)

#     for i, segment in enumerate(segments):
#         print(f"Segment {i + 1}:\n{segment}\n")