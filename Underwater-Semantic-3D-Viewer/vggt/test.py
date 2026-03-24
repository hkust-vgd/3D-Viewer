import torch
import matplotlib.pyplot as plt
from PIL import Image

from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor
from sam3.visualization_utils import *
from torchvision import transforms as TF

model = build_sam3_image_model(load_from_HF=False, checkpoint_path="./sam3.pt")
processor = Sam3Processor(model)
from vggt.utils.load_fn import load_and_preprocess_images

def visualize_tensor(tensor, title="Tensor Visualization"):
    """
    Visualize a (3, H, W) tensor
    
    Args:
        tensor: Can be PyTorch tensor or numpy array
    """
    # Convert to numpy if it's a torch tensor
    if torch.is_tensor(tensor):
        if tensor.is_cuda:
            tensor = tensor.cpu()
        img = tensor.numpy()
    else:
        img = tensor
    
    # Display
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.savefig("dummy.png")

images_vggt = load_and_preprocess_images(["/homes/wctsead/semantic_slam/data/demo/demo1-images/_000.png"])[0].numpy()
image_sam = Image.open("/homes/wctsead/semantic_slam/data/demo/demo1-images/_000.png").convert('RGB')
to_tensor = TF.ToTensor()
image_sam = to_tensor(image_sam)
input(images_vggt.shape)
inference_state = processor.set_image(images_vggt)

inference_state = processor.set_text_prompt(state=inference_state, prompt="coral")

results = inference_state["masks"]
ans = collect_masks(results)
input(ans.shape)
images_vggt = images_vggt.permute(1, 2, 0)
mask = ans != 0
images_vggt[mask] = images_vggt[mask] * 0.4 + ans[mask] * 0.6


visualize_tensor(images_vggt)


# print(len(results))
# for i, mask in enumerate(results):
#     if i > 1:
#         break
#     local_mask = mask.squeeze(0).cpu()
#     mask_img = plot_mask(local_mask)
#     print(mask_img.max())
#     print(mask_img.min())
#     plt.savefig(f"dummy{i}.png")

# plot_results(image, inference_state)
