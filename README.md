# zk-DP

zk-differential privacy project provides an E2E pipeline, under picoZK, to test differential privacy under Zero-Knowledge Proof.

----

## 📖 Setting up

<strong> Option A Use published docker image </strong>

Run this in the command line:
```
docker run --platform linux/amd64 -it hicsail/zk-dp:main      
```

<strong> Option B Clone Repo </strong>

Run this in the command line:
```
git clone git@github.com:hicsail/zk-DP.git
```

Move into the root directory of the project

```
cd zk-DP
```

Inside the root directory, run the build image:

```
docker-compose up -d --build
```

Now you have a brand new container running on your machine



## 🖥️ Getting started

<strong> Enter Docker Shell</strong> 

Since you have a running container, you can subsequently run the following command in your terminal to start Docker Shell:

```
docker exec -it <containerID> bash
```

You can get a containerID from the docker desktop app by clicking the small button highlighted in the red circle
<ul>
    <img width="1161" alt="image" src="https://user-images.githubusercontent.com/62607343/203409123-1a95786f-8b2a-4e71-a920-3a51cf50cf0f.png">
</ul>

If you see something like the following in your command line, you are successfully inside the docker shell
<ul>
<img width="300" alt="image" src="https://user-images.githubusercontent.com/62607343/203413803-19021cb9-07ba-4376-ade0-dbdc6c8506c5.png">
</ul>


<strong> Install wiztoolkit</strong> 

Inside the container, clone wiztoolkit repo and move into wiztoolkit:

(*) You might need to set up ssh key - Follow <a href="https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux"> the instruction </a>

```
git clone git@github.mit.edu:sieve-all/wiztoolkit.git
cd wiztoolkit
```

And run the following commands to install wiztoolkit (Backend for IR0):

```
make
make install
```

## 🏋️‍♀️ Run your Python script and firealarm test module inside the container

You can run your Python script in the docker shell and check the format of statements in the following command:

```
/bin/bash ./run_IR0.sh -f differential_privacy
```

This runs <a href="https://github.com/hicsail/zk-DP/blob/main/differential_privacy.py">   differential_privacy.py</a> and checks format of the output statements.<br>

Alternatively, you can run just the Python statement inside the container:
```
python3 differential_privacy.py
```

## 🧪 Experiment with Different Pseudorandom function


This system utilizes a Pseudorandom Function (PRF) as an integral part of the noise addition process. The current file employs AES as the default PRF. However, you can switch to Triple DES or Poseidon Hash PRF as well in <a href="https://github.com/hicsail/zk-DP/blob/cdb360f8276e12c73c69d4dba7472be12b96c42f/differential_privacy.py#L38_L40"> differential_privacy.py </a>.

<img width="604" alt="image" src="https://github.com/hicsail/zk-DP/assets/62607343/e2ab8f95-ed56-4de5-b4b7-7a90faef7b19">
