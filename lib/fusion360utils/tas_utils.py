import adsk.core
import adsk.fusion
import traceback
import math
app = adsk.core.Application.get()
ui = app.userInterface


#function that will generate tabs for selected edges automatically decides spacing, tabwidth, and number of tabs 
def autoTab(selectedEdges:adsk.core.ObjectCollection,tabWidth_input:adsk.core.ValueCommandInput = None,tabSpacing_input:adsk.core.ValueCommandInput =None,tabOnly = True):
    try:
        #get current component  
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        comp = design.activeComponent
        #make sketch based on one of selected edges (assumes edges are in same plane)
        #TODO add verification that edges are in same plane 
        tEdge:adsk.fusion.BRepEdge = selectedEdges.item(0)
        sketchFace:adsk.fusion.BRepFace = None
        #TODO improve finding of sketchface by looking at face of edge and seeing if they 

        selectedEdges.item(0).length
        if tEdge.faces.item(0).area > tEdge.faces.item(1).area:
            sketchFace = tEdge.faces.item(0)
        else:
            sketchFace = tEdge.faces.item(1)
        
        mt:adsk.fusion.UserParameter = design.userParameters.itemByName("mt")
        if mt == None:
            ui.messageBox("add user parameter 'mt' that specifies material thickness ")
            return

        
        def extrudeProfiles():
                """extrudes all the profiles in the tab sketch """
                extrudes = comp.features.extrudeFeatures
                #creates object collection and adds all profiles to it
                profCollection = adsk.core.ObjectCollection.create()
                for prof in tabSketch.profiles:
                    profCollection.add(prof)
                #specify distance
                dist = adsk.core.ValueInput.createByString(mt.name)
                distanceExtent = adsk.fusion.DistanceExtentDefinition.create(dist)
                 #specify direction
                direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

                #create cut input with all profiles
                cutInput = extrudes.createInput(profCollection,adsk.fusion.FeatureOperations.CutFeatureOperation)
                #specify one directional extrude
                cutInput.setOneSideExtent(distanceExtent,direction)
                #do extrusion by adding it to extrudes
                #exception handling in case there is not body to cut slot into
                if tabOnly == True:
                    try:
                        extrudeFeature = extrudes.add(cutInput)
                    except:
                        ui.messageBox("No body found to cut slot into. Only tabs will be created.")

                    #create extrude input with all profiles
                    extInput: adsk.fusion.ExtrudeFeatureInput = extrudes.createInput(profCollection,adsk.fusion.FeatureOperations.JoinFeatureOperation)
                    #specify joining body
                    extInput.participantBodies = [sketchFace.body]
                    #specify one directional extrude
                    extInput.setOneSideExtent(distanceExtent,direction)
                    #do extrusion by adding it to extrudes
                    extrudeFeature = extrudes.add(extInput)
                elif tabOnly == False:
                    extrudeFeature = extrudes.add(cutInput)
                    #create extrude input with all profiles
                    extInput: adsk.fusion.ExtrudeFeatureInput = extrudes.createInput(profCollection,adsk.fusion.FeatureOperations.JoinFeatureOperation)
                    #specify joining body
                    extInput.participantBodies = [sketchFace.body]
                    #specify one directional extrude
                    extInput.setOneSideExtent(distanceExtent,direction)
                    #do extrusion by adding it to extrudes
                    extrudeFeature = extrudes.add(extInput)

        
        def positionDistanceText(point1:adsk.fusion.SketchPoint,point2:adsk.fusion.SketchPoint):
            """creates 3d point to specify location of text on distance dimension"""
            p1 = point1.worldGeometry
            p2 = point2.worldGeometry
            vec = p1.vectorTo(p2)
            vec.scaleBy(1/2)
            tp = adsk.core.Point3D.create(p1.x,p1.y,p1.z)
            tp.translateBy(vec)
            tsp = tabSketch.modelToSketchSpace(tp)
            
            return tsp

        #draw rectangles provided line 
        def drawLineTabs(line:adsk.fusion.SketchLine):
            """draws the sketch rectangles on a specifed sketch line that are extruded to create tab and slot."""
        
            def calcTabNormal(tabLine):
                """Calculates the "normal" vector for the sketch, that is the vector that is in the plane of the sketch and perpendicular to the edge along which rectangles will be drawn """
                nsp = tabSketch.sketchPoints.add(tabSketch.modelToSketchSpace(tabCenter))
                tabSketch.geometricConstraints.addMidPoint(nsp,tabLine)
                nvec = tabCenter.vectorTo(nsp.worldGeometry)
                nvec.normalize()
                nsp.deleteMe()
                return nvec

            #get the "normal" direction of the sketch
            tabNormal = calcTabNormal(line)

            def addLinePoint(refpoint:adsk.fusion.SketchPoint,distance:str):
                """Adds a sketch point along the tab line at a given distance from a refernce point"""
                sp1 = tabSketch.sketchPoints.add(line.startSketchPoint.geometry)
                tabSketch.geometricConstraints.addCoincident(sp1,line)
                d1 = tabSketch.sketchDimensions.addDistanceDimension(sp1,refpoint,0,positionDistanceText(sp1,refpoint))
                d1.parameter.expression = distance
                return sp1
            
            def addLineRectangle(refpoint:adsk.fusion.SketchPoint,distance:str,tabWidth:str):
                """Adds a sketch rectangle along the tab line a specified width and distance from a reference point"""
                sp1 = addLinePoint(refpoint,distance)
                sp2 = addLinePoint(sp1,tabWidth)
                p3 = adsk.core.Point3D.create(sp2.worldGeometry.x,sp2.worldGeometry.y,sp2.worldGeometry.z)
                p3.translateBy(tabNormal)
                rect = tabSketch.sketchCurves.sketchLines.addThreePointRectangle(sp1,sp2,tabSketch.modelToSketchSpace(p3))
                tabSketch.geometricConstraints.addPerpendicular(tabLine,rect.item(3))
                tabSketch.geometricConstraints.addPerpendicular(tabLine,rect.item(1))
                tabSketch.geometricConstraints.addParallel(tabLine,rect.item(2))
                height = tabSketch.sketchDimensions.addDistanceDimension(rect.item(1).startSketchPoint,rect.item(1).endSketchPoint,0,positionDistanceText(rect.item(1).startSketchPoint,rect.item(1).endSketchPoint))
                height.parameter.expression = mt.expression
            
                return rect
            
            def findNextRefPoint(refpoint:adsk.fusion.SketchPoint,rect:adsk.fusion.SketchLineList):
                """Finds the corner of a sketch rectangle that should be used to position the next sketch recgtangle along line tab"""
                refvec = line.endSketchPoint.worldGeometry.vectorTo(line.startSketchPoint.worldGeometry)
                maxdist = 0
                nextRef:adsk.fusion.SketchPoint = None
                for side in rect:
                    sp = side.startSketchPoint
                    p = sp.worldGeometry
                    v = line.startSketchPoint.worldGeometry.vectorTo(p)
                    if refvec.isParallelTo(v):
                        pdist = line.endSketchPoint.worldGeometry.distanceTo(p)
                        if maxdist <= pdist:
                            maxdist = pdist
                            nextRef = sp
                return nextRef
            
            
            def sketchCenterLine():
                """Adds a sketch line that is perpendicular to the tab line and faces away from the face on which the sketch is"""
                #get the center point of the face which the sketch is on in sketch space
                spoint = tabSketch.modelToSketchSpace(sketchFace.centroid)
                centerSp = tabSketch.sketchPoints.add(spoint)
                tabSketch.geometricConstraints.addMidPoint(centerSp,tabLine)
                centerPoint = adsk.core.Point3D.create(centerSp.worldGeometry.x,centerSp.worldGeometry.y,centerSp.worldGeometry.z)
                centerPoint.translateBy(tabNormal)
                centerLine = tabSketch.sketchCurves.sketchLines.addByTwoPoints(centerSp,tabSketch.modelToSketchSpace(centerPoint))
                tabSketch.geometricConstraints.addPerpendicular(tabLine,centerLine)
                centerLine.isConstruction = True
                return centerLine

            #create center rectangle (used to start when tab quantity odd)
            def sketchCenterRectangle():
                """Adds a sketch rectangle that lies on the tabline and is centered on the tabline. """
                centerLine = sketchCenterLine()
                #create points to define center rectangle
                p1= tabSketch.sketchPoints.add(tabLine.startSketchPoint.geometry)
                tabSketch.geometricConstraints.addCoincident(p1,tabLine)
                p2 = tabSketch.sketchPoints.add(tabLine.endSketchPoint.geometry)
                tabSketch.geometricConstraints.addCoincident(p2,tabLine)
                p3 = adsk.core.Point3D.create(p2.worldGeometry.x,p2.worldGeometry.y,p2.worldGeometry.z)
                p3.translateBy(tabNormal)
                #create 3 point rectangle
                centerRectangle = tabSketch.sketchCurves.sketchLines.addThreePointRectangle(p1,p2,tabSketch.modelToSketchSpace(p3))
                #constrain rectangle
                tabSketch.geometricConstraints.addMidPoint(centerLine.startSketchPoint,centerRectangle.item(0))
                tabSketch.geometricConstraints.addPerpendicular(tabLine,centerRectangle.item(1))
                tabSketch.geometricConstraints.addPerpendicular(tabLine,centerRectangle.item(3))
                tabSketch.geometricConstraints.addParallel(tabLine,centerRectangle.item(2))
                #dimension center rectangle
                tabwid = tabSketch.sketchDimensions.addDistanceDimension(centerRectangle.item(0).startSketchPoint,centerRectangle.item(0).endSketchPoint,0,p3)
                tabwid.value = tabWidth.value
                tabheight = tabSketch.sketchDimensions.addDistanceDimension(centerRectangle.item(1).startSketchPoint,centerRectangle.item(1).endSketchPoint,0,p3)
                tabheight.parameter.expression = mt.name


                return centerRectangle

            #calculate tab spacing depending on specified tab width and spacing settings
            
            if tabWidth_input == None:
                tabWidth = design.userParameters.itemByName("tabWidth")
                if tabWidth == None:
                    tabWidth = design.userParameters.add("tabWidth",adsk.core.ValueInput.createByString(f"3*{mt.name}"),design.unitsManager.defaultLengthUnits,"")
                minTabSpacing = 3*tabWidth.value
            else:
                tabWidth = tabWidth_input
                minTabSpacing = tabSpacing_input.value
                

            maxtabCount = math.floor((line.length-2*mt.value)/(tabWidth.value))
            tabCount = maxtabCount
            tabSpacingVal = (line.length-(2*mt.value)-(tabCount*tabWidth.value))/((tabCount)-1)
            
            while tabSpacingVal <= minTabSpacing and tabCount >1:
                    tabSpacingVal = (line.length-(2*mt.value)-(tabCount*tabWidth.value))/((tabCount)-1)
                    tabCount -= 1

            if tabCount > 1:
                tabSpacing = design.unitsManager.formatInternalValue(tabSpacingVal)
                r1 = addLineRectangle(line.endSketchPoint,mt.name,tabWidth.expression)
                refrect = r1
                refpoint = findNextRefPoint(line.endSketchPoint,refrect)
                for i in range(tabCount):
                    refrect = addLineRectangle(refpoint,tabSpacing,tabWidth.expression)
                    refpoint = findNextRefPoint(line.endSketchPoint,refrect)
            else:
                sketchCenterRectangle()


        #create sketch for tabs
        tabSketch = comp.sketches.addWithoutEdges(sketchFace)
        #project selected edges into tab for sketch 
        tabLines:adsk.fusion.SketchLines = tabSketch.project(selectedEdges)
        #create sketchpoint that will serve as reference to calculate direction that is "normal"
        tabCenter = sketchFace.centroid

        #for each selected edge sketch rectangles are added to the sketch with correct width and spacing
        for tabLine in tabLines:
            tabLine.isConstruction = True
            drawLineTabs(tabLine)
        
        extrudeProfiles()
        
        
    except Exception as error:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

"""Code beyond this point is outdated and not used in current iteration of add-in.
TODO look through this code and delete what is unecessary """

        
def alltest(edgeDist:adsk.core.ValueCommandInput,tabWidth:adsk.core.ValueCommandInput,tabQuantity:adsk.core.IntegerSpinnerCommandInput):
    #get current design and all bodies
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    comp = design.activeComponent
    bodies = comp.bRepBodies
    minEdgeLength = (tabWidth.value+edgeDist.value*2)*tabQuantity.value

    for body in bodies:
        edges = body.edges
        for edge in edges:
            if edge.length >= minEdgeLength:
                drawTab(edge,edgeDist,tabWidth,tabQuantity)

    

def bodyAutoTab(selectedBodies:adsk.fusion.BRepBodies):
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    comp = design.activeComponent
    selectedEdges = adsk.core.ObjectCollection.create()
    mt = design.userParameters.itemByName("mt")
    for body in selectedBodies:
        for face in body.faces:
            facebool = True
            selectedEdges.clear()
            for edge in face.edges:
                if edge.length > 2*mt.value:
                    selectedEdges.add(edge)
                else:
                    facebool = False
                    break
            if facebool:
                autoTab(selectedEdges,tabOnly=True)


    pass
def testAuto():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    comp = design.activeComponent
    bodies = comp.bRepBodies
    selectedEdges = adsk.core.ObjectCollection.create()
    mt = design.userParameters.itemByName("mt")
    for body in bodies:
        for face in body.faces:
            facebool = True
            selectedEdges.clear()
            for edge in face.edges:
                if edge.length > 2*mt.value:
                    selectedEdges.add(edge)
                else:
                    facebool = False
                    break
            if facebool:
                autoTab(selectedEdges)

def drawTab(tEdge:adsk.fusion.BRepEdge,edgeDist:adsk.core.ValueCommandInput,tabWidth:adsk.core.ValueCommandInput,tabQuantity:adsk.core.IntegerSpinnerCommandInput):
    try:
        #define sketches and component
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        comp = design.activeComponent
        sketches = comp.sketches
        
        #get user parameter for material thickness
        mt = design.userParameters.itemByName("mt")

        #face which sketch is on
        sketchFace = None
        #face which tab will be on 
        tabFace = None
        # ui.messageBox(f"area of item 0 is {tEdge.faces.item(0).area}<br>area of item 1 is {tEdge.faces.item(1).area}")
        if tEdge.faces.item(0).area > tEdge.faces.item(1).area:
            sketchFace = tEdge.faces.item(0)
            tabFace = tEdge.faces.item(1)
            # ui.messageBox(f" item 0 is sketchface")
        else:
            sketchFace = tEdge.faces.item(1)
            tabFace = tEdge.faces.item(0)
            # ui.messageBox(f" item 1 is sketchface")

        

        
        #TODO both odd and even sketch behavior need function that fills in specific distance with evenly space rectangles

        #get normal of tab face in global coordinates
        tabNormal = tabFace.evaluator.getNormalAtPoint(tabFace.centroid)[1]


        #define tab sketch
        tabSketch = sketches.addWithoutEdges(sketchFace)


        #get selected edge
        tabLine:adsk.fusion.SketchLine =tabSketch.project(tEdge).item(0)

        #center point of sketch point in sketch space
        spoint = tabSketch.modelToSketchSpace(sketchFace.centroid)
        
        #create center line
        def sketchCenterLine():
        #sanest way to deal with normal vectors is probably to generate points in global space translate them with global space normal vector and then transform points to sketch space when adding to sketch   
            centerSp = tabSketch.sketchPoints.add(spoint)
            tabSketch.geometricConstraints.addMidPoint(centerSp,tabLine)
            centerPoint = adsk.core.Point3D.create(centerSp.worldGeometry.x,centerSp.worldGeometry.y,centerSp.worldGeometry.z)
            centerPoint.translateBy(tabNormal)
            centerLine = tabSketch.sketchCurves.sketchLines.addByTwoPoints(centerSp,tabSketch.modelToSketchSpace(centerPoint))
            tabSketch.geometricConstraints.addPerpendicular(tabLine,centerLine)
            centerLine.isConstruction = True
            return centerLine

        #create center rectangle (used to start when tab quantity odd)
        def sketchCenterRectangle():
            centerLine = sketchCenterLine()
            #create points to define center rectangle
            p1= tabSketch.sketchPoints.add(tabLine.startSketchPoint.geometry)
            tabSketch.geometricConstraints.addCoincident(p1,tabLine)
            p2 = tabSketch.sketchPoints.add(tabLine.endSketchPoint.geometry)
            tabSketch.geometricConstraints.addCoincident(p2,tabLine)
            p3 = adsk.core.Point3D.create(p2.worldGeometry.x,p2.worldGeometry.y,p2.worldGeometry.z)
            p3.translateBy(tabNormal)
            #create 3 point rectangle
            centerRectangle = tabSketch.sketchCurves.sketchLines.addThreePointRectangle(p1,p2,tabSketch.modelToSketchSpace(p3))
            #constrain rectangle
            tabSketch.geometricConstraints.addMidPoint(centerLine.startSketchPoint,centerRectangle.item(0))
            tabSketch.geometricConstraints.addPerpendicular(tabLine,centerRectangle.item(1))
            tabSketch.geometricConstraints.addPerpendicular(tabLine,centerRectangle.item(3))
            tabSketch.geometricConstraints.addParallel(tabLine,centerRectangle.item(2))
            #dimension center rectangle
            tabwid = tabSketch.sketchDimensions.addDistanceDimension(centerRectangle.item(0).startSketchPoint,centerRectangle.item(0).endSketchPoint,0,p3)
            tabwid.value = tabWidth.value
            tabheight = tabSketch.sketchDimensions.addDistanceDimension(centerRectangle.item(1).startSketchPoint,centerRectangle.item(1).endSketchPoint,0,p3)
            tabheight.parameter.expression = mt.name


            return centerRectangle
        
        #create edge rectangles (used to start when tab quantity even)
        def sketchEdgeRectangle(distEdge:int):
            tabLine:adsk.fusion.SketchLine = tabSketch.project(tEdge).item(0)
            #center point in sketch space
            cpoint = tabSketch.modelToSketchSpace(sketchFace.centroid)

            #enables rectangle to be created and both edges 
            #TODO make more generalized and less specific
            edge = None
            if distEdge == 1:
                edge = tabLine.startSketchPoint
            elif distEdge == 0:
                edge = tabLine.endSketchPoint

            #add 3 points to define tab
            #point 1
            p1 = tabSketch.sketchPoints.add(cpoint)
            tabSketch.geometricConstraints.addCoincident(p1,tabLine)
            d1textpoint = adsk.core.Point3D.create(p1.worldGeometry.x,p1.worldGeometry.y,p1.worldGeometry.z)
            d1 =tabSketch.sketchDimensions.addDistanceDimension(p1,edge,0,d1textpoint)
            d1.value = edgeDist.value
            #point 2
            p2 = tabSketch.sketchPoints.add(cpoint)
            tabSketch.geometricConstraints.addCoincident(p2,tabLine)
            d2 =tabSketch.sketchDimensions.addDistanceDimension(p2,p1,0,cpoint)
            d2.value = tabWidth.value
            #point 3
            #normal of tab used to position 3rd point in rectangle tab
            p3 = adsk.core.Point3D.create(p2.worldGeometry.x,p2.worldGeometry.y,p2.worldGeometry.z)
            p3.translateBy(tabNormal)
            #create rectangular tab from 3 point
            r1 = tabSketch.sketchCurves.sketchLines.addThreePointRectangle(p1,p2,tabSketch.modelToSketchSpace(p3))
            #make rectangle edges perpendicular and paralell to tab edge
            tabSketch.geometricConstraints.addPerpendicular(tabLine,r1.item(3))
            tabSketch.geometricConstraints.addPerpendicular(tabLine,r1.item(1))
            tabSketch.geometricConstraints.addParallel(tabLine,r1.item(2))
            d3 = tabSketch.sketchDimensions.addDistanceDimension(r1.item(1).startSketchPoint,r1.item(1).endSketchPoint,0,cpoint)
            d3.parameter.expression = mt.name





        #TODO both odd and even sketch behavior need function that fills in specific distance with evenly space rectangles
        def sketchFillRectangles(startpoint:adsk.fusion.SketchPoint,endpoint:adsk.fusion.SketchPoint):
            pass
       #extrudes all prorfiles in the sketch to a distane mt and joins them to the parent body of tabface
        def extrudeProfiles():
            extrudes = comp.features.extrudeFeatures
            #creates object collection and adds all profiles to it
            profCollection = adsk.core.ObjectCollection.create()
            for prof in tabSketch.profiles:
                profCollection.add(prof)
            #create extrude input with all profiles
            extInput: adsk.fusion.ExtrudeFeatureInput = extrudes.createInput(profCollection,adsk.fusion.FeatureOperations.JoinFeatureOperation)
            #specify joining body
            extInput.participantBodies = [tabFace.body]
            #specify distance
            dist = adsk.core.ValueInput.createByString(mt.name)
            distanceExtent = adsk.fusion.DistanceExtentDefinition.create(dist)
            #specify direction
            direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
            #specify one directional extrude
            extInput.setOneSideExtent(distanceExtent,direction)
            #do extrusion by adding it to extrudes
            extrudeFeature = extrudes.add(extInput)

        #TODO change behavior of sketching depending on whether input is even or odd
        tabqty = tabQuantity.value
        #odd input behavior
        if tabqty%2 == 1:
            #first rectangle centered on edge
            cRec = sketchCenterRectangle() 
            # extrudeProfiles()   
              
            #calculate spacing between subsequent rectangles to get even spacing and necessary edge spacing
            # add in rectangles on one side
            # mirror across center line  
        #even input behavior
        elif tabqty%2 == 0:
            #two rectangles put at specified distance from end
            sketchEdgeRectangle(0)
            sketchEdgeRectangle(1)
            extrudeProfiles()
            
            #get selected edge and its endpoints in sketch 
        
        tabSketch.name = f"{tabFace.body.name} {tabQuantity.value} tab sketch"
    except Exception as error:
        # ui.messageBox("drawTab Failed : " + str(error)) 
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        if tabSketch.isValid == True:
            tabSketch.name = str(error)


def drawTabOld(tface:adsk.fusion.BRepFace):
    try:
        #get active component
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        comp = design.activeComponent


        

        #create sketch for tab profile
        sketches = comp.sketches        
        pararange = tface.evaluator.parametricRange()
        # ui.messageBox(f'x range is {pararange.minPoint.x}-{pararange.maxPoint.x}<br>y range is {pararange.minPoint.y}-{pararange.maxPoint.y}')
        tabsketch = sketches.add(tface)

        def ordersides(curvelist:adsk.fusion.SketchLineList):
            lengthlist = []
            for line in curvelist:
                # ui.messageBox(line.objectType)
                lengthlist.append([line.length,line])
            lengthlist.sort(key=lambda x:x[0])
            return lengthlist
        
        ll = ordersides(tabsketch.sketchCurves)
        
        #find midpoint of face
        midx = (pararange.minPoint.x+pararange.maxPoint.x)/2
        midy = (pararange.minPoint.y+pararange.maxPoint.y)/2
        midpoint = adsk.core.Point2D.create(midx,midy)
        
        #get center of face in global coordinate space
        (retVal,cpoint) =tface.evaluator.getPointAtParameter(midpoint)
        #convert global coordinates to sketch coordinates
        spoint = tabsketch.modelToSketchSpace(cpoint)

        #create two point rectangle
        r1 = tabsketch.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(spoint.x+1,spoint.y+2,spoint.z),adsk.core.Point3D.create(spoint.x-1,spoint.y-2,spoint.z))
        #order sides of rectangle by length so that long side can be selected
        r1ll = ordersides(r1)
        #select opposite corner points
        r1p1 = r1ll[2][1].startSketchPoint
        r1p2 = r1ll[3][1].startSketchPoint
        
        #long edges of face
        l1 = ll[2][1]
        l2 = ll[3][1]

        #short edges of face 
        l3 = ll[0][1]
        l4 = ll[1][1]
        # ui.messageBox("object type is: "+str(l1.objectType))
        # ui.messageBox("object type is: "+str(r1p1.objectType))
        
        tabsketch.geometricConstraints.addCoincident(r1p1,l1)
        tabsketch.geometricConstraints.addCoincident(r1p2,l2)





    





        '''this way is too much work I want to do it easier'''
        # #find midpoint of face
        # midx = (pararange.minPoint.x+pararange.maxPoint.x)/2
        # midy = (pararange.minPoint.y+pararange.maxPoint.y)/2
        # midpoint = adsk.core.Point2D.create(midx,midy)
        
        # #get center of face in global coordinate space
        # (retVal,cpoint) =tface.evaluator.getPointAtParameter(midpoint)
        # #convert global coordinates to sketch coordinates
        # spoint = tabsketch.modelToSketchSpace(cpoint)

        # #constrain points to midpoints of short side of rectangle and create line
        # mp1 = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # tabsketch.geometricConstraints.addMidPoint(mp1,lengthlist[0][1])
        # mp2 = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # tabsketch.geometricConstraints.addMidPoint(mp2,lengthlist[1][1])
        # mline = tabsketch.sketchCurves.sketchLines.addByTwoPoints(mp1,mp2)
        # mline.isConstruction = True

        # # #contrain points to midpoint of long side of rectangle and create line
        # # mp3 = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # # tabsketch.geometricConstraints.addMidPoint(mp3,lengthlist[2][1])
        # # mp4 = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # # tabsketch.geometricConstraints.addMidPoint(mp4,lengthlist[3][1])
        # # mline = tabsketch.sketchCurves.sketchLines.addByTwoPoints(mp3,mp4)
        # # mline.isConstruction = True

        # mt = design.userParameters.itemByName("mt")
        

        # #create rectangles for tabs
        # rc1 = tabsketch.sketchPoints.add(spoint)
        # tabsketch.geometricConstraints.addHorizontalPoints(rc1,mp1)
        # rc1dim = tabsketch.sketchDimensions.addDistanceDimension(rc1,mp1,adsk.fusion.DimensionOrientations.AlignedDimensionOrientation,spoint)



            
        
        
        
        

        #get center of face using intersecting lines like user would with gui
        # ui.messageBox(f'sketch has {tabsketch.sketchCurves.count} sketch curves')
        # ui.messageBox(f'{tabsketch.sketchCurves.item(0).objectType}')


        

        mt = design.userParameters.itemByName("mt")
        
        # #TODO dimension and contrain center point so that its position updates when parameters change
        # #create sketch circle centered on face and with radius mt/2
        # circle = tabsketch.sketchCurves.sketchCircles.addByCenterRadius(spoint,mt.value/2)
        # circle.isConstruction = True
        # #point where text goes needs to be in sketch space but cannot be at the same spot as center point
        # textpoint = adsk.core.Point3D.create(spoint.x+mt.value,spoint.y+mt.value,spoint.z) 
        # circdiam:adsk.fusion.SketchDimension = tabsketch.sketchDimensions.addDiameterDimension(circle,textpoint)
        # circdiam.parameter.expression = mt.name

        # #check curves circle intersects with, used to find longer edges of face
        # longLines:adsk.fusion.SketchCurves =circle.intersections(None)[1]
        # #create midline 
        # m1point = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # tabsketch.geometricConstraints.addMidPoint(m1point,longLines.item(0)) 
        # m2point = tabsketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        # tabsketch.geometricConstraints.addMidPoint(m2point,longLines.item(1)) 
        # mline = tabsketch.sketchCurves.sketchLines.addByTwoPoints(m1point,m2point)
        # mline.isConstruction = True
    
        
        # #create geometrically constrained midpoint
        # mpoint = tabsketch.sketchPoints.add(adsk.core.Point3D.create(1,0,0))
        # tabsketch.geometricConstraints.addMidPoint(mpoint,mline)

        # #delete circle used for finding midpoint
        # circle.deleteMe()

        #TODO adding more constrained points so that tab rectangles can be added in geometrically constrained


        # #get profile for extrusion
        # prof = tabsketch.profiles.item(0)
        
    



        # #extrusion
        # extrudes = comp.features.extrudeFeatures
        # extInput: adsk.fusion.ExtrudeFeatureInput = extrudes.createInput(prof,adsk.fusion.FeatureOperations.JoinFeatureOperation)
        # dist = adsk.core.ValueInput.createByString(mt.name)
        # distanceExtent = adsk.fusion.DistanceExtentDefinition.create(dist)
        # direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
        # extInput.setOneSideExtent(distanceExtent,direction)
        # extrudeFeature = extrudes.add(extInput)
        # tabBody = extrudeFeature.bodies.item(0)
        # propl = []
        # i = 0
        # for prop in tabBody.appearance.appearanceProperties:
        #     propl.append([prop.name,i])
        #     i+=1



    except Exception as error:
        # ui.messageBox("drawTab Failed : " + str(error)) 
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        return None

def drawTabPreview(tface:adsk.fusion.BRepFace,tlength):
    #TODO make preview look like extrude cut so it is easy to see placement of slot and tab
    try:
        #get active component
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        comp = design.activeComponent


        

        #create sketch for tab profile
        sketches = comp.sketches        
        pararange = tface.evaluator.parametricRange()
        # ui.messageBox(f'x range is {pararange.minPoint.x}-{pararange.maxPoint.x}<br>y range is {pararange.minPoint.y}-{pararange.maxPoint.y}')
        tabsketch = sketches.addWithoutEdges(tface)

        #get center of face using intersecting lines like user would with gui
        # ui.messageBox(f'sketch has {tabsketch.sketchCurves.count} sketch curves')
        # ui.messageBox(f'{tabsketch.sketchCurves.item(0).objectType}')


        #find midpoint of face
        midx = (pararange.minPoint.x+pararange.maxPoint.x)/2
        midy = (pararange.minPoint.y+pararange.maxPoint.y)/2
        midpoint = adsk.core.Point2D.create(midx,midy)
        

        #get center of face in global coordinate space
        (retVal,cpoint) =tface.evaluator.getPointAtParameter(midpoint)
        #convert global coordinates to sketch coordinates
        spoint = tabsketch.modelToSketchSpace(cpoint)

        mt = design.userParameters.itemByName("mt")
        
        #TODO dimension and constrain center point so that its position updates when parameters change
        #create sketch circle centered on face and with radius mt/2
        circle = tabsketch.sketchCurves.sketchCircles.addByCenterRadius(spoint,mt.value/2)
        textpoint = adsk.core.Point3D.create(midx-2*mt.value,midy,0) #TODO change to sketch coordinates so sketch is offset reasonably
        circdiam:adsk.fusion.SketchDimension = tabsketch.sketchDimensions.addDiameterDimension(circle,textpoint)
        circdiam.parameter.expression = mt.name
    

        #get profile for extrusion
        prof = tabsketch.profiles.item(0)
        
    



        #extrusion
        extrudes = comp.features.extrudeFeatures
        extInput: adsk.fusion.ExtrudeFeatureInput = extrudes.createInput(prof,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        dist = adsk.core.ValueInput.createByString(tlength.expression)
        distanceExtent = adsk.fusion.DistanceExtentDefinition.create(dist)
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
        extInput.setOneSideExtent(distanceExtent,direction)
        extrudeFeature = extrudes.add(extInput)
        tabBody = extrudeFeature.bodies.item(0)
        # propl = []
        # i = 0
        # for prop in tabBody.appearance.appearanceProperties:
        #     propl.append([prop.name,i])
        #     i+=1
        adsk.core
        bodyColor:adsk.core.ColorProperty = tabBody.appearance.appearanceProperties.item(1)
        tabBody.appearance.appearanceProperties
        red =adsk.core.Color.create(255,0,0,125)
        bodyColor.value = red
        bodyColor
        # ui.messageBox(str(bodyColor.value.getColor()))



    except Exception as error:
        # ui.messageBox("drawTab Failed : " + str(error)) 
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        return None