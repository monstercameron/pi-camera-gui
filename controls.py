# need to make pure functions, down with side effects and objects!!

# still has side effect
def save_to_app(app, property, value):
    app[property] = value
    return app[property]

# need to refactor
def adjust_by_factor(app, factor, property, min_max):
    if factor > 0:
        updated_value = app[property] * factor
        print(property, ": ", app[property])

        if updated_value > min_max[1]:
            app[property] = min_max[1]
            return app[property]
        else:
            app[property] = updated_value
            return app[property]
    elif factor < 0:
        updated_value = app[property] // abs(factor)
        print(property, ": ", app[property])

        if updated_value < min_max[0]:
            app[property] = min_max[0]
            return min_max[0]
        else:
            app[property] = updated_value
            return app[property]
    else:
        print('Error')

# need to refactor
def adjust_by_increment(app, increment, property, min_max):
    if increment > 0:
        updated_value = app[property] + increment
        print(property, ": ", app[property])

        if updated_value > min_max[1]:
            app[property] = min_max[1]
            return app[property]
        else:
            app[property] = updated_value
            return app[property]
    elif increment < 0:
        updated_value = app[property] - abs(increment)
        print(property, ": ", app[property])

        if updated_value < min_max[0]:
            app[property] = min_max[0]
            return min_max[0]
        else:
            app[property] = updated_value
            return app[property]
    else:
        print('Error')


def traverse_list(current, direction, list):
    if direction == 'next':
        index = list.index(current)
        if index + 1 > len(list) - 1:
            index = 0
            return list[index]
        else:
            return list[index+1]
    elif direction == 'previous':
        index = list.index(current)
        if index - 1 < 0:
            index = len(list)-1
            return list[index]
        else:
            return list[index-1]
