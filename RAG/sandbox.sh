openshell sandbox create \
  --gpu \
  --from openshell-community/sandboxes/ollama \
  --resource axelera.ai/aipu=1 \
  --host-device /dev/axelera0 \
  --name algic-agent-sandbox
