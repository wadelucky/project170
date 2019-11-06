# CS170 Project Guavabot

a.py, b.py, c.py, c(1).py are different versions of our solver

## How to Use

To test locally, please do the following:
Run the local server using **python local_server.py** in terminal. 

This will start a web server that your client will now connect to. It will pick a random input instance to serve. An instance is a set of parameters (such as bot locations or student correctness) of the problem.

In a separate terminal, run **python client.py --solver solver**. The --solver flag indicates the solver python file the client should use. It's the file name of your solver, with .py omitted.

