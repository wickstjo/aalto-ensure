sudo nano kepler.sh && sudo chmod +x kepler.sh && sudo ./kepler.sh
echo -e "\n"##########################################################################################"\n"

# CLONE THE KEPLER REPO
# git clone --depth 1 git@github.com:sustainable-computing-io/kepler.git
git clone --depth 1 https://github.com/sustainable-computing-io/kepler
cd kepler

# REFRESH GO-LANG REF
export PATH=$PATH:/usr/local/go/bin
go version

echo -e "\n"##########################################################################################"\n"


make build-manifest

# COMPILE & DEPLOY KEPLER MANIFESTS
make build-manifest OPTS="CI_DEPLOY PROMETHEUS_DEPLOY"
kubectl apply -f _output/generated-manifest/deployment.yaml


kubectl get pods -A --watch