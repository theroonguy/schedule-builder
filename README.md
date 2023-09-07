# UMD Schedule Builder and Visualizer
Schedule builder and visualizer specifically for UMD courses that considers sleep hours, professor preferences, extracurricular activities, and more.

## Priorities
The schedule builder lets the user enter in a set of priorities, where the first constraints will take priority over the latter constraints.

Options:
1. Earliest class start
2. Latest class end

## Process
1. Grab course, section, and professor data from the [student-run UMD API](https://umd.io).
2. Search for sections according to priorities, and avoid overlapping classes.
3. Create a schedule from selected sections.
4. Visualize schedule using ftorres16's [my_weekly_schedule](https://github.com/ftorres16/my_weekly_schedule/tree/main).
