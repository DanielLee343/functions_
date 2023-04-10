import json
# import os
from time import time
# import shutil
import torch
import torch.nn as nn
import torch.optim as optim
import boto3
import os
# import torchvision.transforms as transforms
# from torch.utils.data import DataLoader

# import function.dummy as dummy
import function.global_settings as settings
from function.utils import get_network, get_training_dataloader, get_test_dataloader, WarmUpLR, \
    most_recent_folder, most_recent_weights, last_epoch, best_acc_weights

def train(net, optimizer, loss_function, cifar100_training_loader, warmup_scheduler, bs, batches, epoch):

    start = time()
    net.train()
    for batch_index, (images, labels) in enumerate(cifar100_training_loader):

        # if args.gpu:
        #     labels = labels.cuda()
        #     images = images.cuda()

        optimizer.zero_grad()
        outputs = net(images)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()

        n_iter = (epoch - 1) * len(cifar100_training_loader) + batch_index + 1

        last_layer = list(net.children())[-1]
        # for name, para in last_layer.named_parameters():
        #     if 'weight' in name:
        #         writer.add_scalar('LastLayerGradients/grad_norm2_weights', para.grad.norm(), n_iter)
        #     if 'bias' in name:
        #         writer.add_scalar('LastLayerGradients/grad_norm2_bias', para.grad.norm(), n_iter)

        print('Training Epoch: {epoch} [{trained_samples}/{total_samples}]\tLoss: {:0.4f}\tLR: {:0.6f}'.format(
            loss.item(),
            optimizer.param_groups[0]['lr'],
            epoch=epoch,
            trained_samples=batch_index * bs + len(images),
            total_samples=len(cifar100_training_loader.dataset)
        ))

        #update training loss for each iteration
        # writer.add_scalar('Train/loss', loss.item(), n_iter)

        if epoch <= 1:
            warmup_scheduler.step()
        if (batch_index * bs + len(images)) > batches:
            break

    # for name, param in net.named_parameters():
    #     layer, attr = os.path.splitext(name)
    #     attr = attr[1:]
    #     writer.add_histogram("{}/{}".format(layer, attr), param, epoch)

    finish = time()
    time_used = finish - start

    print('epoch {} training time consumed: {:.2f}'.format(epoch, time_used))
    return time_used

@torch.no_grad()
def eval_training(net, cifar100_test_loader, loss_function, epoch=0, tb=True):

    start = time()
    net.eval()

    test_loss = 0.0 # cost function error
    correct = 0.0

    for (images, labels) in cifar100_test_loader:

        # if args.gpu:
        #     images = images.cuda()
        #     labels = labels.cuda()

        outputs = net(images)
        loss = loss_function(outputs, labels)

        test_loss += loss.item()
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum()

    finish = time()
    # if args.gpu:
    #     print('GPU INFO.....')
    #     print(torch.cuda.memory_summary(), end='')
    # print('Evaluating Network.....')
    # print('Test set: Epoch: {}, Average loss: {:.4f}, Accuracy: {:.4f}, Time consumed: {:.2f}'.format(
    #     epoch,
    #     test_loss / len(cifar100_test_loader.dataset),
    #     correct.float() / len(cifar100_test_loader.dataset),
    #     finish - start
    # ))
    # print()

    #add informations to tensorboard
    # if tb:
    #     writer.add_scalar('Test/Average loss', test_loss / len(cifar100_test_loader.dataset), epoch)
    #     writer.add_scalar('Test/Accuracy', correct.float() / len(cifar100_test_loader.dataset), epoch)

    return correct.float() / len(cifar100_test_loader.dataset)

def do_train(net, bs, lr, batches):
    cifar100_training_loader = get_training_dataloader(
        settings.CIFAR100_TRAIN_MEAN,
        settings.CIFAR100_TRAIN_STD,
        num_workers=4,
        batch_size=bs,
        shuffle=True
    )

    cifar100_test_loader = get_test_dataloader(
        settings.CIFAR100_TRAIN_MEAN,
        settings.CIFAR100_TRAIN_STD,
        num_workers=4,
        batch_size=bs,
        shuffle=True
    )

    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    train_scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=settings.MILESTONES, gamma=0.2) #learning rate decay
    iter_per_epoch = len(cifar100_training_loader)
    warmup_scheduler = WarmUpLR(optimizer, iter_per_epoch * 1)

    # checkpoint_path = os.path.join(settings.CHECKPOINT_PATH, net_name, settings.TIME_NOW)

    #create checkpoint folder to save model
    # if not os.path.exists(checkpoint_path):
    #     os.makedirs(checkpoint_path)
    # checkpoint_path = os.path.join(checkpoint_path, '{net}-{epoch}-{type}.pth')

    best_acc = 0.0
    for epoch in range(1, settings.EPOCH + 1):
        # print("epoch: ", epoch)
        if epoch > 1:
            train_scheduler.step(epoch)

        # if args.resume:
        #     if epoch <= resume_epoch:
        #         continue

        time_used = train(net, optimizer, loss_function, cifar100_training_loader, warmup_scheduler, bs, batches, epoch)
        # acc = eval_training(epoch)
        # acc = eval_training(net, cifar100_test_loader, loss_function, epoch)

        #start to save best performance model after learning rate decay to 0.01
        # if epoch > settings.MILESTONES[1] and best_acc < acc:
        #     weights_path = checkpoint_path.format(net=net_name, epoch=epoch, type='best')
        #     print('saving weights file to {}'.format(weights_path))
        #     torch.save(net.state_dict(), weights_path)
        #     best_acc = acc
        #     continue

        # if not epoch % settings.SAVE_EPOCH:
        #     weights_path = checkpoint_path.format(net=net_name, epoch=epoch, type='regular')
        #     print('saving weights file to {}'.format(weights_path))
        #     torch.save(net.state_dict(), weights_path)
    # os.remove('./resnet50_dataset.zip')
    # shutil.rmtree('./data')
    return time_used

def get_weights(net_name):
    f_access_id = open("/var/openfaas/secrets/access-id", "r")
    access_id = f_access_id.read()
    f_access_id.close()
    f_secret_key = open("/var/openfaas/secrets/secret-key", "r")
    secret_key = f_secret_key.read()
    f_secret_key.close()

    download_path = "./" + net_name + ".pth"
    if os.path.isfile(download_path) == False:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_id,
            aws_secret_access_key=secret_key
        )
        input_bucket = "lyuze"
        object_key = "dl_workload/" + net_name + ".pth"
        s3_client.download_file(input_bucket, object_key, download_path)
    return download_path

def do_serve(net, net_name, batches, bs=16):
    cifar100_test_loader = get_test_dataloader(
        settings.CIFAR100_TRAIN_MEAN,
        settings.CIFAR100_TRAIN_STD,
        #settings.CIFAR100_PATH,
        num_workers=4,
        batch_size=16,
    )
    # download weight from s3
    iter_to_serve = batches / bs
    weight_path = get_weights(net_name)
    net.load_state_dict(torch.load(weight_path))
    print(net)
    net.eval()
    correct_1 = 0.0
    correct_5 = 0.0
    total = 0
    start = time()
    with torch.no_grad():
        for n_iter, (image, label) in enumerate(cifar100_test_loader):
            # only serve 1/10 of the whole test set
            if n_iter + 1 > iter_to_serve:
                break
            print("iteration: {}\ttotal {} iterations".format(n_iter + 1, len(cifar100_test_loader)))

            # if args.gpu:
            #     image = image.cuda()
            #     label = label.cuda()
            #     print('GPU INFO.....')
            #     print(torch.cuda.memory_summary(), end='')


            output = net(image)
            _, pred = output.topk(5, 1, largest=True, sorted=True)

            label = label.view(label.size(0), -1).expand_as(pred)
            correct = pred.eq(label).float()

            #compute top 5
            correct_5 += correct[:, :5].sum()

            #compute top1
            correct_1 += correct[:, :1].sum()
    time_used = time() - start
    # if args.gpu:
    #     print('GPU INFO.....')
    #     print(torch.cuda.memory_summary(), end='')

    # print()
    # print("Top 1 err: ", 1 - correct_1 / len(cifar100_test_loader.dataset))
    # print("Top 5 err: ", 1 - correct_5 / len(cifar100_test_loader.dataset))
    # print("Parameter numbers: {}".format(sum(p.numel() for p in net.parameters())))
    # clean up
    # shutil.rmtree('./data')
    # os.remove(weight_path)
    print("serve time used:", time_used)
    return time_used

def handle(req):
    payload = json.loads(req)
    train_or_serve = payload['task']
    net_name = "squeezenet"
    bs = 128
    lr = 1e-2
    batches = 1000

    if 'net' in payload:
        net_name = payload['net']
    if 'bs' in payload:
        bs = int(payload['bs'])
    if 'lr' in payload:
        lr = float(payload['lr'])
    if 'batches' in payload:
        batches = int(payload['batches'])

    # dummy.dummy_func()
    net = get_network(net_name)

    if train_or_serve == 'train':
        time_used = do_train(net, bs, lr, batches)
    elif train_or_serve == 'serve':
        time_used = do_serve(net, net_name, batches, 16)
    
    return time_used
