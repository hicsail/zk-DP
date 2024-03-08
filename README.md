# zk-DP

This zk-differential privacy repository provides an E2E pipeline, supported by picozk, to test differential privacy under Zero-Knowledge Proof.

----

## Quick Navigation

- [Use Docker](#-use-docker)
- [Run Locally](#-run-locally)
- [Variety of PRF](#-variety-of-prf)

## 🐳 [Use Docker](#-use-docker)


#### 🚧 Build Docker Image and Run Container

<i> <strong> Option A Use published docker image </strong> </i> 

Run this line of code in the command line:

```
docker run --platform linux/amd64 -it hicsail/zk-dp:main      
```

<i> <strong> Option B Clone Repo </strong> </i> 

Run the following in the command line to get the container up and running:
```
git clone git@github.com:hicsail/zk-DP.git     # Clone the repository
cd zk-DP                                       # Move into the root directory of the project
docker-compose up -d --build                   # Inside the root directory, run the build image:
```

#### 🖥️ Getting started

<i> <strong> Step1: Enter Docker Shell</strong> </i> 

Since you have a running container, you can subsequently run the following command in your terminal to start Docker Shell:

```
docker exec -it <containerID> bash
```

You can get a container-ID from the docker desktop app by clicking the small button highlighted in the red circle
<ul>
    <img width="1161" alt="image" src="https://user-images.githubusercontent.com/62607343/203409123-1a95786f-8b2a-4e71-a920-3a51cf50cf0f.png">
</ul>

If you see something like the following in your command line, you are successfully inside the docker shell
<ul>
<img width="300" alt="image" src="https://user-images.githubusercontent.com/62607343/203413803-19021cb9-07ba-4376-ade0-dbdc6c8506c5.png">
</ul>


<i> <strong> Step2: Install wiztoolkit</strong> </i> 

We are using Fire Alarm, one of wiztoolkit packages.
After entering the container, clone wiztoolkit repo and run the following commands to install wiztoolkit:

(* You might need to set up ssh key - Follow <a href="https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux"> the instruction </a>)

```
git clone git@github.mit.edu:sieve-all/wiztoolkit.git
cd wiztoolkit
make
make install
```


### 🏋️‍♀️ Run the shell script

Now all setups are done for you to run your Python script inside the docker shell.
Run the following command in the docker shell, and you will see the Python script,<a href="https://github.com/hicsail/zk-DP/blob/main/differential_privacy.py">   differential_privacy.py</a>, generating zk statements and fire-alarm checks the format of the statements:

```
/bin/bash ./run_IR0.sh -f differential_privacy
```

## 👨‍💻 [Run Locally](#-run-locally)

This option doesn't require Docker, while it focuses on running the Python scripts, skipping setting Fire Alarm.

Run this in the command line:
```
git clone git@github.com:hicsail/zk-DP.git
```

Move into the root directory of the project and install dependencies

```
cd zk-DP
cp ./consts/poseidon_hash.py ./picozk/picozk/poseidon_hash/poseidon_hash.py
python3 -m venv venv           # or pypy3 -m venv myenv
source venv/bin/activate       # or source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install picozk/.
```

The following will run the main file:
```
python3 differential_privacy.py  # or pypy3 differential_privacy.py
```

## 🧪 [Variety of PRF](#-variety-of-prf)

This system utilizes a Pseudorandom Function (PRF) as an integral part of the noise addition process. The current file employs AES as the default PRF. However, you can switch to Triple DES or Poseidon Hash PRF as well in <a href="https://github.com/hicsail/zk-DP/blob/cdb360f8276e12c73c69d4dba7472be12b96c42f/differential_privacy.py#L38_L40"> differential_privacy.py </a>.

<img width="604" alt="image" src="https://github.com/hicsail/zk-DP/assets/62607343/e2ab8f95-ed56-4de5-b4b7-7a90faef7b19">
