import math

import cv2
import numpy as np
from matplotlib import pyplot

CIRCLE_RADIUS = 20
TEXT_MARGIN = 5
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.5
FONT_THICKNESS = 1


def plotTableWithCircles(numberOfColumns, numberOfRows, tableCells, filepath):
    # Calculate sizes.
    allCircles = tableCells.values()
    maxCirclesInCell = max(len(circles) for circles in allCircles)

    circlesPerRowInCell = int(math.ceil(math.sqrt(maxCirclesInCell)))
    circlesPerColumnInCell = circlesPerRowInCell

    cellWidth = circlesPerRowInCell * 2*CIRCLE_RADIUS
    cellHeight = circlesPerColumnInCell * 2*CIRCLE_RADIUS

    tableWidth = numberOfColumns * cellWidth
    tableHeight = numberOfRows * cellHeight

    # Create a white image
    img = np.empty((tableWidth, tableHeight, 3), np.uint8)
    img[:] = 255

    # Plot table.
    for i in range(0, tableWidth, cellWidth):
        img = cv2.line(img, (0, i), (tableHeight - 1, i), (0, 0, 0), 1)

    for j in range(0, tableHeight, cellHeight):
        img = cv2.line(img, (j, 0), (j, tableWidth - 1), (0, 0, 0), 1)

    # Plot circles.
    for cell, circles in tableCells.items():
        cellColumnOneBased, cellRowOneBased = cell
        cellColumn = cellColumnOneBased - 1
        cellRow = cellRowOneBased - 1

        # Break list of circles in current cell into a table.
        arrangedCircles = [circles[i:i+circlesPerRowInCell] for i in range(0, len(circles), circlesPerRowInCell)]

        # Iterate all rows in current cell's circles table.
        for j, circleRow in enumerate(arrangedCircles):
            # Iterate all circles in current row of circles in current cell.
            for i, circleData in enumerate(circleRow):
                circleTitle, circleColor = circleData
                titleColor = tuple(255 - x for x in circleColor)

                # Calculate center of current circle.
                circleCenterX = cellColumn * cellWidth + i * 2*CIRCLE_RADIUS + CIRCLE_RADIUS
                circleCenterY = cellRow * cellHeight + j * 2*CIRCLE_RADIUS + CIRCLE_RADIUS

                # Draw circle.
                img = cv2.circle(img, (circleCenterX, circleCenterY), CIRCLE_RADIUS, circleColor, -1)

                # Draw title.
                ((textWidth, textHeight), _) = cv2.getTextSize(circleTitle, FONT_FACE, FONT_SCALE, FONT_THICKNESS)
                cv2.putText(img, circleTitle, (circleCenterX - textWidth // 2, circleCenterY + textHeight // 2), FONT_FACE, FONT_SCALE, titleColor, FONT_THICKNESS, cv2.LINE_AA)

    # Calculate axis width and height.
    longestRowIndexSample = int(math.floor(math.log10(int(numberOfRows))) + 1) * '5'
    ((maxTextWidth, maxTextHeight), _) = cv2.getTextSize(longestRowIndexSample, FONT_FACE, FONT_SCALE, FONT_THICKNESS)
    axisWidth = maxTextWidth + 2*TEXT_MARGIN
    axisHeight = maxTextHeight + 2*TEXT_MARGIN

    # Expand image to add room for axis.
    for i in range(axisHeight):
        img = np.insert(img, 0, (255, 255, 255), 0)

    for i in range(axisWidth):
        img = np.insert(img, 0, (255, 255, 255), 1)

    # Add axis numbers.
    for i in range(int(numberOfRows)):
        indexText = '{index}'.format(index=i+1)
        ((textWidth, textHeight), _) = cv2.getTextSize(indexText, FONT_FACE, FONT_SCALE, FONT_THICKNESS)
        cv2.putText(img, indexText, (axisWidth + i * cellWidth + cellWidth // 2 - textWidth // 2, axisHeight - TEXT_MARGIN), FONT_FACE, FONT_SCALE, (0, 0, 0), FONT_THICKNESS, cv2.LINE_AA)

    for j in range(int(numberOfColumns)):
        indexText = '{index}'.format(index=j+1)
        ((textWidth, textHeight), _) = cv2.getTextSize(indexText, FONT_FACE, FONT_SCALE, FONT_THICKNESS)
        cv2.putText(img, indexText, (axisWidth // 2 - textWidth // 2, axisHeight + j * cellHeight + cellHeight // 2 + textHeight // 2), FONT_FACE, FONT_SCALE, (0, 0, 0), FONT_THICKNESS, cv2.LINE_AA)

    # Plot.
    cv2.imwrite(filepath, img)
    #cv2.imshow('Table', img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
