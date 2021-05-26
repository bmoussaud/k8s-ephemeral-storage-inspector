1. Clone the repo by running `git clone -b tutorial https://github.com/microsoft/python-sample-vscode-flask-tutorial.git`
  2. In VS Code Terminal, run `python3 -m venv env` to create a virtual environment as described in the tutorial.
  3. Press Ctrl + Shift + P and run command `Python: Select Interpreter`. If possible, select the interpreter ending with "('env': venv)"
  4. Activate the virtual environment by running `env/scripts/activate` if you are on Windows or run `source env/bin/activate` if you are
  on Linux/MacOS.
  5. In terminal, run `pip install flask`.
  6. From Run and Debug section, select `Python: Flask` launch configuration and hit F5.


  1. python3 -m venv env
  2. Press Ctrl + Shift + P and run command `Python: Select Interpreter`. If possible, select the interpreter ending with "('env': venv)"
  3. Activate the virtual environment by running `chmod +x  env/bin/activate && env/bin/activate` if you are on Windows or run `source env/bin/activate` if you are
  on Linux/MacOS.
  4. In terminal, run `pip3 install flask`.
  5. From Run and Debug section, select `Python: Flask` launch configuration and hit F5.



  1. Create namespace `filler` : `kubectl create ns filler`
  2. Deploy `kubectl apply -f k8s -n filler`
  3. Expose: `kubectl -n filler port-forward svc/fillapp-service 5000`
  4. Actions

  * Fill: curl http://localhost:5000/api/fill/5
  
