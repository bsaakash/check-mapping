#
# Copyright (c) 2023 Leland Stanford Junior University
# Copyright (c) 2023 The Regents of the University of California
#
# This file is part of pelicun.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# You should have received a copy of the BSD 3-Clause License along with
# pelicun. If not, see <http://www.opensource.org/licenses/>.
#
# Contributors:
# Adam Zsarnóczay
# Aakash Bangalore Satish

import json
from pathlib import Path

import jsonschema
from jsonschema import validate
import pandas as pd

def auto_populate(aim):
    """
    Automatically creates a performance model for PGA-based Hazus EQ analysis.

    Parameters
    ----------
    AIM: dict
        Asset Information Model - provides features of the asset that can be
        used to infer attributes of the performance model.

    Returns
    -------
    gi: dict
        The GI from the input AIM. Kept for backwards-compatibility, will be 
        removed eventually.
        TODO(adamzs): remove this output once all auto-pop scripts have been
        replaced by mapping scripts.
    dl_ap: dict
        Damage and Loss parameters - these define the performance model and
        details of the calculation.
    comp: DataFrame
        Component assignment - Defines the components (in rows) and their
        location, direction, and quantity (in columns).
    """

    # extract the General Information
    gi = aim.get('GeneralInformation')

    # load the schema assuming it is called "input_schema.json" and it is
    # stored next to the mapping script
    current_file_path = Path(__file__)
    current_directory = current_file_path.parent

    with Path(current_directory/"input_schema.json").open(
        encoding='utf-8'
    ) as f:
        input_schema = json.load(f)

    # validate the provided features against the required inputs
    try:
        validate(instance=gi, schema=input_schema)
    except jsonschema.exceptions.ValidationError as exc:
        msg = ('The provided building information does not conform to the input'
               ' requirements for the chosen damage and loss model.')
        raise ValueError(msg) from exc

    # prepare the labels for model IDs
    building_type = gi['BuildingType']

    design_level_map = {
        'Pre-Code': 'PC',
        'Low-Code': 'LC',
        'Moderate-Code': 'MC',
        'High-Code': 'HC'
    }
    design_level = design_level_map[gi['DesignLevel']]

    height_class_map = {
        'Low-Rise': 'L',
        'Mid-Rise': 'M',
        'High-Rise': 'H'
    }
    height_class = gi.get('HeightClass')

    if height_class is not None:
        model_id = f'LF.{building_type}.{height_class}.{design_level}'
    else:
        model_id = f'LF.{building_type}.{design_level}'

    comp = pd.DataFrame(
        {f'{model_id}': ['ea',         1,          1,        1,   'N/A']},  # noqa: E241
        index = ['Units','Location','Direction','Theta_0','Family']  # noqa: E231, E251
    ).T

    # if needed, add components to simulate damage from ground failure
    if gi["GroundFailure"]:

        foundation_type_map = {
            'Shallow': 'S',
            'Deep': 'D'
        }
        foundation_type = foundation_type_map[gi['FoundationType']]

        gf_model_id_h = f'GF.H.{foundation_type}'
        gf_model_id_v = f'GF.V.{foundation_type}'

        comp_gf = pd.DataFrame(
            {f'{gf_model_id_h}':[  'ea',         1,          1,        1,   'N/A'],  # noqa: E201, E231, E241
             f'{gf_model_id_v}':[  'ea',         1,          3,        1,   'N/A']},  # noqa: E201, E231, E241
            index = [     'Units','Location','Direction','Theta_0','Family']  # noqa: E201, E231, E251
        ).T

        comp = pd.concat([comp, comp_gf], axis=0)

    # get the occupancy class
    occupancy_type = gi['OccupancyClass']    

    dl_ap = {
        'Asset': {
            'ComponentAssignmentFile': 'CMP_QNT.csv',
            'ComponentDatabase': 'Hazus Earthquake - Buildings',
            'NumberOfStories': 1,  # there is only one component in a building-level resolution
            'OccupancyType': f'{occupancy_type}',
            'PlanArea': '1',  # TODO(adamzs): check if this is even needed
        },
        'Damage': {'DamageProcess': 'Hazus Earthquake'},
        'Demands': {},
        'Losses': {
            'Repair': {
                'ConsequenceDatabase': 'Hazus Earthquake - Buildings',
                'MapApproach': 'Automatic',
            }
        },
        'Options': {
            'NonDirectionalMultipliers': {'ALL': 1.0},
        },
    }

    return gi, dl_ap, comp

