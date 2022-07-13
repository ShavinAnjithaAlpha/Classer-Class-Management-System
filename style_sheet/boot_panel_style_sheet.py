style_sheet = """
    
    
    QWidget#main {
            background-image : url(resources/images/wallpaper.jpg);
            background-position : center center;
            background-repeat : no-repeat;
            background-fill : cover;
            
            }

    QLabel {
            color : white;
            font-size : 22px;
            font-weight : 100;}
            
    QLabel#title-label {
            color : white;
            font-size : 100px;
            font-weight : 500;}
            
    QLabel#date-label {
        font-size : 75px;
        font-weight : 60;
        color : white;
    }
    
    QLabel#time-label {
        font-size : 170px;
        font-weight : 70;
        color : white;
    }
    
    QPushButton#connect-btn {
            border-radius : 25px;
            font-size : 23px;
            font-weight : 400;}
    
    QLineEdit {width : 300px;
                border-radius : 2px;
                background-color : rgba(0, 0, 0, 0.0);
                border : none;
                border-bottom : 2px solid rgba(255, 255, 255, 0.5);
                color : white;
                font-size : 22px;}
                
    QLineEdit:focus {border-bottom : 2px solid white;}
    
    QGroupBox::title {color : white;
                    font-size : 25px;
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                   /* position at the top center */
                    padding: 10px 5px;
                    }
                    
    QGroupBox {
        font-size : 23px;
        padding : 70px 35px 30px 30px;
        border-radius : 20px;
        background-color : rgba(0, 0, 0, 0.5)}
        
    QMessageBox QLabel {
            color : black;
            font-size : 17px;
            }
        
"""