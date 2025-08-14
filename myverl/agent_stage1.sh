#!/bin/bash

ulimit -n 65535

! pip install json_repair
! pip install fire

export PYTHONUNBUFFERED=1
export HYDRA_FULL_ERROR=1
# export VLLM_ATTENTION_BACKEND=XFORMERS # vllm0.8.2 no need

RUN_NAME=Qwen2.5-7B_ppo_from_base_stage1_agent_0621

# your wandb account
export WANDB_API_KEY="xxx"
export WANDB_ENTITY="xxx"
export WANDB_PROJECT="PilotRL"
export WANDB_NAME=$RUN_NAME
export WANDB_MODE="online"

CHECKPOINT_DIR="$CHECKPOINT_SAVE/checkpoints/$RUN_NAME"
WANDB_DIR="$CHECKPOINT_SAVE/wandb/$RUN_NAME"

rm -rf $CHECKPOINT_DIR
rm -rf $WANDB_DIR

export WANDB_DIR=$WANDB_DIR

if [ ! -d $CHECKPOINT_DIR ]; then
    mkdir -p $CHECKPOINT_DIR
fi

if [ ! -d $WANDB_DIR ]; then
    mkdir -p $WANDB_DIR
fi

wandb login --relogin $WANDB_API_KEY

export DIAGNOSIS_VERIFY_URL="xxx" # fill in the verification model's url

master_ip=$(python ./examples/get_domain_ip.py $MASTER_ADDR)
curr_ip=$(python ./examples/get_host_ip.py)
echo $master_ip $curr_ip

if [ "$master_ip" = "$curr_ip" ]; then
    echo "run ray!!!!!!!!!!!!!!!!!"
    ray start \
        --head \
        --dashboard-host 0.0.0.0 \
        --dashboard-port=8066 \
        --node-manager-port=6380 \
        --object-manager-port=6381 \
        --runtime-env-agent-port=6382 \
        --dashboard-agent-grpc-port=6383 \
        --metrics-export-port=6384 \
        --min-worker-port=10010 \
        --max-worker-port=11010 \
        --redis-shard-ports=8266 \
        --dashboard-grpc-port=8267 \
        --port=6379
    sleep 200s
    echo "start job!!!!!!!!!!!!!!!!!"
    ray job submit \
        --address="$master_ip:6379" \
        -- python -u -m verl.trainer.main_ppo \
            hydra.run.dir=. \
            hydra.output_subdir=null \
            hydra/job_logging=disabled \
            hydra/hydra_logging=disabled \
            data.train_files=/data/agent/code/myverl/data/train/agent_mixture.parquet \
            data.val_files=/data/agent/code/myverl/data/train/agent_mixture.parquet \
            data.train_batch_size=256 \
            data.max_prompt_length=2048 \
            data.max_response_length=14336 \
            data.truncation=left \
            data.reward_fn_key=reward_actor \
            actor_rollout_ref.model.path=/data/opensource/Qwen2.5-7B-Instruct \
            actor_rollout_ref.actor.optim.lr=1e-6 \
            actor_rollout_ref.actor.ppo_mini_batch_size=64 \
            actor_rollout_ref.actor.fsdp_config.param_offload=True \
            actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
            actor_rollout_ref.model.enable_gradient_checkpointing=True \
            actor_rollout_ref.rollout.name=vllm_with_agent_stage1 \
            actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
            actor_rollout_ref.rollout.gpu_memory_utilization=0.8 \
            actor_rollout_ref.rollout.max_num_batched_tokens=16384 \
            actor_rollout_ref.actor.grad_clip=1.0 \
            actor_rollout_ref.actor.ulysses_sequence_parallel_size=2 \
            actor_rollout_ref.rollout.n=16 \
            actor_rollout_ref.rollout.temperature=1.0 \
            actor_rollout_ref.model.use_remove_padding=True \
            actor_rollout_ref.actor.use_dynamic_bsz=True \
            actor_rollout_ref.actor.ppo_max_token_len_per_gpu=32768 \
            algorithm.adv_estimator=grpo \
            actor_rollout_ref.actor.loss_agg_mode=token-mean \
            actor_rollout_ref.actor.entropy_coeff=0.0 \
            actor_rollout_ref.actor.use_kl_loss=False \
            actor_rollout_ref.actor.kl_loss_coef=0.0 \
            algorithm.use_kl_in_reward=False \
            algorithm.kl_ctrl.kl_coef=0.0 \
            algorithm.lam=1.0 \
            actor_rollout_ref.actor.clip_ratio=0.2 \
            actor_rollout_ref.actor.clip_ratio_low=0.2 \
            actor_rollout_ref.actor.clip_ratio_high=0.2 \
            actor_rollout_ref.actor.clip_ratio_c=3.0 \
            trainer.val_before_train=False \
            reward_model.reward_manager=diagnosis_with_agent \
            actor_rollout_ref.rollout.val_kwargs.top_k=-1 \
            actor_rollout_ref.rollout.val_kwargs.top_p=0.9 \
            actor_rollout_ref.rollout.val_kwargs.temperature=0.6 \
            actor_rollout_ref.rollout.val_kwargs.n=4 \
            actor_rollout_ref.rollout.val_kwargs.do_sample=True \
            data.filter_overlong_prompts=True \
            data.filter_overlong_prompts_workers=2 \
            +reward_model.reward_kwargs.overlong_buffer_cfg.enable=True \
            +reward_model.reward_kwargs.overlong_buffer_cfg.len=3072 \
            +reward_model.reward_kwargs.overlong_buffer_cfg.penalty_factor=1.0 \
            +reward_model.reward_kwargs.overlong_buffer_cfg.log=False \
            +reward_model.reward_kwargs.max_resp_len=14336 \
            +reward_model.reward_kwargs.save_path=$CHECKPOINT_SAVE/reward/$RUN_NAME \
            trainer.critic_warmup=0 \
            trainer.default_hdfs_dir=null \
            trainer.n_gpus_per_node=8 \
            trainer.nnodes=2 \
            trainer.save_freq=8 \
            trainer.test_freq=-1 \
            trainer.logger=['console','wandb'] \
            trainer.total_epochs=1 \
            trainer.project_name=$WANDB_PROJECT \
            trainer.experiment_name=$RUN_NAME \
            trainer.default_local_dir=$CHECKPOINT_DIR | tee $CHECKPOINT_SAVE/$RUN_NAME-$(date +%m-%d-%H).log
else
    sleep 30s
    ray start \
        --address $master_ip:6379 \
        --node-manager-port=6380 \
        --object-manager-port=6381 \
        --runtime-env-agent-port=6382 \
        --dashboard-agent-grpc-port=6383 \
        --metrics-export-port=6384 \
        --min-worker-port=10010 \
        --max-worker-port=11010 \
        --block
fi

sleep 30d