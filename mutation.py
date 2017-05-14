#!/usr/bin/env python2
# -*- coding : utf8 -*-
# Copyright 2016 (c) Daro Heng <daro.heng@u-psud.fr>, Aris Tritas <aris.tritas@u-psud.fr>
# Licence: BSD 3 clause
""" Some mutation operators for evolution strategies. """

from __future__ import division

from traceback import format_exc

from numpy import power, abs, multiply
from numpy import seterr
from numpy import zeros, ones, sqrt, exp
from numpy.linalg import norm
from numpy.random import randn

seterr(all='raise')


def derandomized_mutation(x, sigma, n_dimensions):
    """ Adaptation of the variance with both global and dimension-wise components.
        :sigma : vector of step-sizes and/or standard deviations
        :reference : Nikolaus Hansen, Dirk V. Arnold and Anne Auger,
        Evolution Strategies, February 2015. (Algorithm 3)
        """
    try:
        # Initialize variables
        d = sqrt(n_dimensions)
        tau = 1 / 3
        global_noise = tau * randn()
        z = randn(n_dimensions)
        one = ones(n_dimensions)

        # Mutate vector
        xRes = x + exp(global_noise) * multiply(sigma, z)
        # Compute sigma adaptation
        adaptation_vect = exp((abs(z) - one) / n_dimensions)
        # Compute new value of sigma
        adapted_sigma = multiply(sigma, adaptation_vect) * exp(global_noise / d)
    except FloatingPointError | RuntimeWarning | ValueError:
        print(format_exc())
        exit(2)

    return xRes, adapted_sigma


def search_path_mutation(sigma, local_mutations, n_dimensions, mu, lamda):
    """ (mu/mu, lambda)-ES with Search Path Algorithm
        :reference : Nikolaus Hansen, Dirk V. Arnold and Anne Auger,
        Evolution Strategies, February 2015. (Algorithm 4)

        :param sigma: vector of step-sizes and/or standard deviations
        :param local_mutations: matrix of (n_offsprings, n_dimensions)
        sampled from the standard normal distribution
        :param lamda: number of offsprings
        :param mu: number of parents
        :param n_dimensions: dimensions of the search space
        :return: the adapted variance
    """

    search_path = zeros(n_dimensions)  # exponentially fading record of mutation steps
    c = sqrt(mu / (n_dimensions + 4))
    d = 1 + sqrt(mu / n_dimensions)
    di = 3 * n_dimensions
    one = ones(n_dimensions)

    search_path *= (1 - c)
    search_path += sqrt(c * (2 - c)) * sqrt(mu) / mu * local_mutations.sum(axis=0)
    sigma_abs = exp((abs(search_path) - one) / di)
    sigma_norm = exp((norm(search_path) - 1) * (c / d))
    sigma = multiply(sigma, sigma_abs) * sigma_norm

    return sigma


def one_fifth_success(sigma, offspring_fitness, parent_fitness, inv_dim_sqrt):
    """ Adapt step-size using the 1/5-th rule, :references [Retchenberg, Schumer, Steiglitz]
    The idea is to raise, in expectation, the log of the variance if the success probability
        is larger than 1/5, and decrease it otherwise. Note: for our fitness function bigger is better
        :param sigma: initial variance
        :param offspring_fitness: fitness value of the child
        :param parent_fitness: fitness value of the parent
        :return: adapted variance
        :param inv_dim_sqrt: inversed of the square root of problem dimension.
        """
    indicator = int(parent_fitness <= offspring_fitness)
    sigma *= power(exp(indicator - 0.2), inv_dim_sqrt)
    return sigma
