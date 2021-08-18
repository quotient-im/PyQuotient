import QtQuick 2.6
import QtQuick.Controls 2.1
// import QtQuick.Controls.Styles 2.1

ToolButton {
    width: visible * implicitWidth
    height: visible * parent.height
    anchors.top: parent.top
    anchors.rightMargin: 2

    // style: ButtonStyle {
    //     label: Text {
    //         text: control.text
    //         font: settings.font
    //         fontSizeMode: Text.VerticalFit
    //         minimumPointSize: settings.font.pointSize - 3
    //         verticalAlignment: Text.AlignVCenter
    //         horizontalAlignment: Text.AlignHCenter
    //         renderType: settings.render_type
    //     }
    // }
}
