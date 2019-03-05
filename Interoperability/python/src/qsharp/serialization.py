#!/bin/env python
# -*- coding: utf-8 -*-
##
# serialization.py: Utilities for mapping C# values to and from JSON.
##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

import numpy as np

# Tuples are json encoded differently in C#, this makes sure they are in the right format.
def preserialize(obj):
    """
    Given a Python object to be serialized, converts that object to a form ready
    to be serialized. For instance, any tuples to are converted to dictionaries
    of a form expected by the Q# backend, and any NumPy arrays are transformed
    to ordinary Python lists.
    """
    if isinstance(obj, np.ndarray):
        result = [
            preserialize(element)
            for element in obj
        ]
        return result

    if isinstance(obj, tuple):
        result = {
            '@type': 'tuple'
        }
        for i in range(len(obj)):
            result[f"item{i+1}"] = preserialize(obj[i])
        return result

    elif isinstance(obj, list):
        result = []
        for i in obj:
            result.append(preserialize(i))
        return result

    elif isinstance(obj, dict):
        result = {}
        for i in obj:
            result[i] = preserialize(obj[i])
        return result

    else:
        return obj

def unmap_tuples(obj):
    """
    Given a Python object deserialized from JSON, converts any dictionaries that
    represent tuples back to Python tuples. Dictionaries are considered to be
    tuples if they either contain a key `@type` with the value `tuple`, or if
    they have a key `item1`.
    """
    if isinstance(obj, dict):
        # Does this dict represent a tuple?
        if obj.get('@type', None) in ('tuple', '@tuple') or 'item1' in obj:
            values = []
            while True:
                item = f"Item{len(values) + 1}"
                if item in obj:
                    values.append(unmap_tuples(obj[item]))
                else:
                    break
            return tuple(values)
        # Since this is a plain dict, unmap its values and we're good.
        return {
            key: unmap_tuples(value)
            for key, value in obj.items()
        }

    elif isinstance(obj, list):
        return [unmap_tuples(value) for value in obj]

    else:
        return obj
