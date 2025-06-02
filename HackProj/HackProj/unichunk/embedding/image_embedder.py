# Image Embedder using CLIP (ViT-B/32)
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

class ImageEmbedder:
    def __init__(self, model_name='openai/clip-vit-base-patch32'):
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def embed(self, images):
        inputs = self.processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            embeddings = self.model.get_image_features(**inputs)
        return embeddings.cpu().numpy()
