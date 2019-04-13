import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
import numpy as np


class Policy_net:
    def __init__(self, name: str, env):
        """
        策略网络
        :param name: string
        :param env: env
        """

        ob_space = env.observation_space
        ob_agent_space = env.observation_agent_space
        ob_other_space = env.observation_other_space
        act_space = env.action_space

        with tf.variable_scope(name):
            # self.obs = tf.placeholder(dtype=tf.float32, shape=(None, ob_space), name='obs')
            self.obs_agent = tf.placeholder(dtype=tf.float32, shape=(None, ob_agent_space), name='obs_agent')
            self.obs_other = tf.placeholder(dtype=tf.float32, shape=(None, ob_other_space), name='obs_other')
            self.obs_agent_l1 =  tf.layers.dense(inputs=self.obs_agent, units=100, activation=tf.nn.selu)
            self.obs_other_l1 = tf.layers.dense(inputs=self.obs_other, units=50, activation=tf.nn.selu)
            self.obs = tf.concat([self.obs_agent_l1, self.obs_other_l1], axis=1)
            with tf.variable_scope('policy_net'):
                layer_1 = tf.layers.dense(inputs=self.obs, units=200, activation=tf.nn.selu)
                layer_2 = tf.layers.dense(inputs=layer_1, units=100, activation=tf.nn.selu)
                layer_3 = tf.layers.dense(inputs=layer_2, units=act_space, activation=tf.nn.selu)
                self.act_probs = tf.layers.dense(inputs=layer_3, units=act_space, activation=tf.nn.softmax)

            with tf.variable_scope('value_net'):
                layer_1 = tf.layers.dense(inputs=self.obs, units=100, activation=tf.nn.selu)
                layer_2 = tf.layers.dense(inputs=layer_1, units=50, activation=tf.nn.selu)
                self.v_preds = tf.layers.dense(inputs=layer_2, units=1, activation=None)

            self.act_stochastic = tf.multinomial(tf.log(self.act_probs+0.00001), num_samples=1)
            self.act_stochastic = tf.reshape(self.act_stochastic, shape=[-1])

            self.act_deterministic = tf.argmax(self.act_probs, axis=1)

            self.scope = tf.get_variable_scope().name

    def act(self, obs, stochastic=True):
        """
        Action
        :param obs: observations
        :param stochastic: 随机策略或确定性策略
        :return: action, value
        """
        feed_dict = {
            self.obs_agent : [obs[0][0:20]],
            self.obs_other : [obs[0][-7:]]
        }
        # feed_dict = {
        #     self.obs: obs
        # }
        if stochastic:
            # 符合多项式分布采样的结果
            return tf.get_default_session().run([self.act_stochastic, self.v_preds], feed_dict=feed_dict)
        else:
            # 网络决策出来的值
            return tf.get_default_session().run([self.act_deterministic, self.v_preds], feed_dict=feed_dict)

    def get_action_prob(self, obs):
        """
        获取策略网络的softmax输出
        :param obs:
        :return:
        """
        feed_dict = {
            self.obs_agent: [obs[0][0:20]],
            self.obs_other: [obs[0][-7:]]
        }
        # feed_dict = {
        #     self.obs: obs
        # }
        return tf.get_default_session().run(self.act_probs, feed_dict=feed_dict)

    def get_variables(self):
        """
        获取GLOBAL变量
        :return:
        """
        return tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.scope)

    def get_trainable_variables(self):
        """
        获取TRAINABLE变量
        :return:
        """
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self.scope)
