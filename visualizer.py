import os

"""
Name
Day of week [Mon, Tue, Wed, Thu, Fri]
01:00 - 15:00
color
"""

def gen_text(schedule):
    output = ""

    for day in schedule:
        for block in schedule[day]:
            block_text = ""
            block_text += f"{block['id']}\n"

            if day == "M": block_text += f"Mon\n"
            elif day == "Tu": block_text += f"Tue\n"
            elif day == "W": block_text += f"Wed\n"
            elif day == "Th": block_text += f"Thu\n"
            elif day == "F": block_text += f"Fri\n"

            format = "%H:%M"
            start = block['start_time'].strftime(format)
            end = block['end_time'].strftime(format)
            block_text += f"{start} - {end}\n"

            block_text += "lightblue\n\n"
            output += block_text
    
    with open('schedule.txt', 'w') as f:
        f.write(output)

def visualize():
    os.system("my_weekly_schedule schedule.txt")