pkill -9 kubectl
kubectl rollout status -n openfaas deploy/gateway
kubectl port-forward -n openfaas svc/gateway 8080:8080 &

sleep 2

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

# sudo chmod 666 /var/run/docker.sock

# sync; echo 3 | sudo tee /proc/sys/vm/drop_caches 