from torch.autograd import Variable
import torch.onnx
import torchvision
import torch

dummy_input = Variable(torch.randn(16, 3, 640, 640))
model = torch.hub.load('C:/Users/vasilchenkodv/PycharmProjects/CVphoto/', 'custom',
                            path='C:/Users/vasilchenkodv/PycharmProjects/CVphoto/bestPCB2.pt', source='local')['model']
torch.onnx.export(model, dummy_input, "C:/Users/vasilchenkodv/PycharmProjects/CVphoto/pytorch_model.onnx")