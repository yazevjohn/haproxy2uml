# haproxy2uml
Convert HAproxy config 2 UML diagram

# Reguirements
```bash
bash$ pip install -r requirements.txt
```
# Usage

- usage example
```bash
python main.py --config_file 'haproxy.cfg' 
```

- filter usage example
```bash
python main.py --config_file 'haproxy.cfg' --frontend 'unsecured'
```