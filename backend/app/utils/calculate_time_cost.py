def calculate_time_cost(current_timer):
    new_timer = current_timer - 1
    new_cost = ((15 - new_timer)) ** (15 - new_timer)
    return new_cost
