def compute_success_ratio(contents, artefacts):
    """Compute ratio between number identified regions and extra content

    Args:
        contents (list): list of identified regions
        artefacts (dict): artefact per service

    Returns:
        float: success ratio
    """
    num_of_identified = len(contents)
    max_artefacts = max([len(items) for items in artefacts.values()])
    return {'identified': num_of_identified, 
            'artefacts': max_artefacts, 
            'ratio': num_of_identified/max_artefacts}
