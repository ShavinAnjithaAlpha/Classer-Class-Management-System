style_sheet = """
    
    
    QWidget#bootup-panel QWidget#main {
            background-color : white;
            background-image : url(resources/images/wallpaper.jpg);
            background-position : center center;
            background-repeat : no-repeat;
            background-fill : cover;
            
            }

    QWidget#bootup-panel QLabel {
            color : white;
            font-size : 22px;
            font-weight : 100;}
            
    QWidget#bootup-panel QLabel#title-label {
            color : white;
            font-size : 100px;
            font-weight : 500;}
            
    QWidget#bootup-panel QLabel#date-label {
        font-size : 75px;
        font-weight : 60;
        color : white;
    }

    QWidget#bootup-panel QLabel#time-label {
        font-size : 170px;
        font-weight : 70;
        color : white;
    }

    
    QWidget#login-panel QPushButton#connect-btn {
            border-radius : 25px;
            font-size : 23px;
            font-weight : 400;}
    
    QWidget#login-panel QLineEdit {width : 300px;
                border-radius : 2px;
                background-color : rgba(0, 0, 0, 0.0);
                border : none;
                border-bottom : 2px solid rgba(255, 255, 255, 0.5);
                color : white;
                font-size : 22px;}
                
    QWidget#login-panel QLineEdit:focus {border-bottom : 2px solid white;}
    
    QWidget#login-panel QGroupBox::title {color : white;
                    font-size : 25px;
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                   /* position at the top center */
                    padding: 10px 5px;
                    }
                    
    QWidget#login-panel QGroupBox {
        font-size : 23px;
        padding : 70px 35px 30px 30px;
        border-radius : 20px;
        background-color : rgba(0, 0, 0, 0.5)}
        
    QWidget#login-panel QMessageBox QLabel {
            color : black;
            font-size : 17px;
            }
        
"""