from typing import TypedDict, Union, Optional, Dict, Callable
from streamsync.ui_manager import StreamsyncUI
from streamsync.core_ui import Component
  

RootProps = TypedDict('RootProps', {
    "appName": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "emptinessColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "selectedColor": str,
    "cssClasses": str,
    "contentWidth": str,
    "contentHAlign": str,
    "contentVAlign": str,
    "contentPadding": str
}, total=False)

RootEventHandlers = TypedDict('RootEventHandlers', {
    "ss-hashchange": Union[str, Callable]
}, total=False)

PageProps = TypedDict('PageProps', {
    "key": str,
    "pageMode": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "emptinessColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "selectedColor": str,
    "cssClasses": str
}, total=False)

PageEventHandlers = TypedDict('PageEventHandlers', {
    "ss-keydown": Union[str, Callable],
    "ss-page-open": Union[str, Callable]
}, total=False)

SidebarProps = TypedDict('SidebarProps', {
    "startCollapsed": str,
    "sidebarBackgroundColor": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

SidebarEventHandlers = TypedDict('SidebarEventHandlers', {
}, total=False)

ButtonProps = TypedDict('ButtonProps', {
    "text": str,
    "isDisabled": str,
    "tooltip": str,
    "tooltipLocation": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "icon": str,
    "buttonShadow": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

ButtonEventHandlers = TypedDict('ButtonEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

TextProps = TypedDict('TextProps', {
    "text": str,
    "useMarkdown": str,
    "tooltip": str,
    "tooltipLocation": str,
    "alignment": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

TextEventHandlers = TypedDict('TextEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

SectionProps = TypedDict('SectionProps', {
    "title": str,
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

SectionEventHandlers = TypedDict('SectionEventHandlers', {
}, total=False)

HeaderProps = TypedDict('HeaderProps', {
    "text": str,
    "accentColor": str,
    "emptinessColor": str,
    "cssClasses": str
}, total=False)

HeaderEventHandlers = TypedDict('HeaderEventHandlers', {
}, total=False)

HeadingProps = TypedDict('HeadingProps', {
    "text": str,
    "headingType": str,
    "alignment": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

HeadingEventHandlers = TypedDict('HeadingEventHandlers', {
}, total=False)

DataFrameProps = TypedDict('DataFrameProps', {
    "dataframe": str,
    "showIndex": str,
    "enableSearch": str,
    "enableDownload": str,
    "displayRowCount": Union[float, str],
    "wrapText": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "separatorColor": str,
    "dataframeBackgroundColor": str,
    "dataframeHeaderRowBackgroundColor": str,
    "fontStyle": str,
    "cssClasses": str
}, total=False)

DataFrameEventHandlers = TypedDict('DataFrameEventHandlers', {
}, total=False)

HTMLElementProps = TypedDict('HTMLElementProps', {
    "element": str,
    "styles": Union[Dict, str],
    "attrs": Union[Dict, str],
    "htmlInside": str,
    "cssClasses": str
}, total=False)

HTMLElementEventHandlers = TypedDict('HTMLElementEventHandlers', {
}, total=False)

PaginationProps = TypedDict('PaginationProps', {
    "page": Union[float, str],
    "pageSize": Union[float, str],
    "totalItems": Union[float, str],
    "pageSizeOptions": str,
    "pageSizeShowAll": str,
    "jumpTo": str
}, total=False)

PaginationEventHandlers = TypedDict('PaginationEventHandlers', {
    "ss-change-page": Union[str, Callable],
    "ss-change-page-size": Union[str, Callable]
}, total=False)

RepeaterProps = TypedDict('RepeaterProps', {
    "repeaterObject": Union[Dict, str],
    "keyVariable": str,
    "valueVariable": str
}, total=False)

RepeaterEventHandlers = TypedDict('RepeaterEventHandlers', {
}, total=False)

ColumnProps = TypedDict('ColumnProps', {
    "title": str,
    "width": Union[float, str],
    "isSticky": str,
    "isCollapsible": str,
    "startCollapsed": str,
    "separatorColor": str,
    "contentPadding": str,
    "contentHAlign": str,
    "contentVAlign": str,
    "cssClasses": str
}, total=False)

ColumnEventHandlers = TypedDict('ColumnEventHandlers', {
}, total=False)

ColumnContainerProps = TypedDict('ColumnContainerProps', {
    "cssClasses": str
}, total=False)

ColumnContainerEventHandlers = TypedDict('ColumnContainerEventHandlers', {
}, total=False)

TabProps = TypedDict('TabProps', {
    "name": str,
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

TabEventHandlers = TypedDict('TabEventHandlers', {
}, total=False)

TabContainerProps = TypedDict('TabContainerProps', {
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

TabContainerEventHandlers = TypedDict('TabContainerEventHandlers', {
}, total=False)

LinkProps = TypedDict('LinkProps', {
    "url": str,
    "target": str,
    "rel": str,
    "text": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

LinkEventHandlers = TypedDict('LinkEventHandlers', {
}, total=False)

HorizontalStackProps = TypedDict('HorizontalStackProps', {
    "contentPadding": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

HorizontalStackEventHandlers = TypedDict('HorizontalStackEventHandlers', {
}, total=False)

SeparatorProps = TypedDict('SeparatorProps', {
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SeparatorEventHandlers = TypedDict('SeparatorEventHandlers', {
}, total=False)

ImageProps = TypedDict('ImageProps', {
    "src": str,
    "caption": str,
    "tooltip": str,
    "tooltipLocation": str,
    "maxWidth": Union[float, str],
    "maxHeight": Union[float, str],
    "secondaryTextColor": str,
    "cssClasses": str
}, total=False)

ImageEventHandlers = TypedDict('ImageEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

PDFProps = TypedDict('PDFProps', {
    "source": str,
    "highlights": Union[Dict, str],
    "selectedMatch": Union[float, str],
    "page": Union[float, str],
    "controls": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

PDFEventHandlers = TypedDict('PDFEventHandlers', {
}, total=False)

IFrameProps = TypedDict('IFrameProps', {
    "src": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

IFrameEventHandlers = TypedDict('IFrameEventHandlers', {
    "ss-load": Union[str, Callable]
}, total=False)

GoogleMapsProps = TypedDict('GoogleMapsProps', {
    "apiKey": str,
    "mapId": str,
    "mapType": str,
    "zoom": Union[float, str],
    "lat": Union[float, str],
    "lng": Union[float, str],
    "markers": Union[Dict, str],
    "cssClasses": str
}, total=False)

GoogleMapsEventHandlers = TypedDict('GoogleMapsEventHandlers', {
    "gmap-marker-click": Union[str, Callable],
    "gmap-click": Union[str, Callable]
}, total=False)

MapboxProps = TypedDict('MapboxProps', {
    "accessToken": str,
    "mapStyle": str,
    "zoom": Union[float, str],
    "lat": Union[float, str],
    "lng": Union[float, str],
    "markers": Union[Dict, str],
    "controls": str,
    "cssClasses": str
}, total=False)

MapboxEventHandlers = TypedDict('MapboxEventHandlers', {
    "mapbox-marker-click": Union[str, Callable],
    "mapbox-click": Union[str, Callable]
}, total=False)

IconProps = TypedDict('IconProps', {
    "icon": str,
    "tooltip": str,
    "tooltipLocation": str,
    "size": Union[float, str],
    "color": str,
    "cssClasses": str
}, total=False)

IconEventHandlers = TypedDict('IconEventHandlers', {
}, total=False)

TimerProps = TypedDict('TimerProps', {
    "intervalMs": Union[float, str],
    "isActive": str,
    "accentColor": str,
    "cssClasses": str
}, total=False)

TimerEventHandlers = TypedDict('TimerEventHandlers', {
    "ss-tick": Union[str, Callable]
}, total=False)

TextInputProps = TypedDict('TextInputProps', {
    "label": str,
    "placeholder": str,
    "passwordMode": str,
    "cssClasses": str
}, total=False)

TextInputEventHandlers = TypedDict('TextInputEventHandlers', {
    "ss-change": Union[str, Callable],
    "ss-change-finish": Union[str, Callable]
}, total=False)

TextInputBindings = TypedDict('TextInputBindings', {
    "ss-change": str
}, total=False)

TextareaInputProps = TypedDict('TextareaInputProps', {
    "label": str,
    "placeholder": str,
    "rows": Union[float, str],
    "cssClasses": str
}, total=False)

TextareaInputEventHandlers = TypedDict('TextareaInputEventHandlers', {
    "ss-change": Union[str, Callable],
    "ss-change-finish": Union[str, Callable]
}, total=False)

TextareaInputBindings = TypedDict('TextareaInputBindings', {
    "ss-change": str
}, total=False)

NumberInputProps = TypedDict('NumberInputProps', {
    "label": str,
    "placeholder": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "valueStep": Union[float, str],
    "cssClasses": str
}, total=False)

NumberInputEventHandlers = TypedDict('NumberInputEventHandlers', {
    "ss-number-change": Union[str, Callable],
    "ss-number-change-finish": Union[str, Callable]
}, total=False)

NumberInputBindings = TypedDict('NumberInputBindings', {
    "ss-number-change": str
}, total=False)

SliderInputProps = TypedDict('SliderInputProps', {
    "label": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "stepSize": Union[float, str],
    "cssClasses": str
}, total=False)

SliderInputEventHandlers = TypedDict('SliderInputEventHandlers', {
    "ss-number-change": Union[str, Callable]
}, total=False)

SliderInputBindings = TypedDict('SliderInputBindings', {
    "ss-number-change": str
}, total=False)

DateInputProps = TypedDict('DateInputProps', {
    "label": str,
    "cssClasses": str
}, total=False)

DateInputEventHandlers = TypedDict('DateInputEventHandlers', {
    "ss-date-change": Union[str, Callable]
}, total=False)

DateInputBindings = TypedDict('DateInputBindings', {
    "ss-date-change": str
}, total=False)

RadioInputProps = TypedDict('RadioInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "orientation": str,
    "cssClasses": str
}, total=False)

RadioInputEventHandlers = TypedDict('RadioInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

RadioInputBindings = TypedDict('RadioInputBindings', {
    "ss-option-change": str
}, total=False)

CheckboxInputProps = TypedDict('CheckboxInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "orientation": str,
    "cssClasses": str
}, total=False)

CheckboxInputEventHandlers = TypedDict('CheckboxInputEventHandlers', {
    "ss-options-change": Union[str, Callable]
}, total=False)

CheckboxInputBindings = TypedDict('CheckboxInputBindings', {
    "ss-options-change": str
}, total=False)

DropdownInputProps = TypedDict('DropdownInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "cssClasses": str
}, total=False)

DropdownInputEventHandlers = TypedDict('DropdownInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

DropdownInputBindings = TypedDict('DropdownInputBindings', {
    "ss-option-change": str
}, total=False)

SelectInputProps = TypedDict('SelectInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "placeholder": str,
    "maximumCount": Union[float, str],
    "accentColor": str,
    "chipTextColor": str,
    "selectedColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SelectInputEventHandlers = TypedDict('SelectInputEventHandlers', {
    "ss-option-change": Union[str, Callable]
}, total=False)

SelectInputBindings = TypedDict('SelectInputBindings', {
    "ss-option-change": str
}, total=False)

MultiselectInputProps = TypedDict('MultiselectInputProps', {
    "label": str,
    "options": Union[Dict, str],
    "placeholder": str,
    "maximumCount": Union[float, str],
    "accentColor": str,
    "chipTextColor": str,
    "selectedColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

MultiselectInputEventHandlers = TypedDict('MultiselectInputEventHandlers', {
    "ss-options-change": Union[str, Callable]
}, total=False)

MultiselectInputBindings = TypedDict('MultiselectInputBindings', {
    "ss-options-change": str
}, total=False)

FileInputProps = TypedDict('FileInputProps', {
    "label": str,
    "allowMultipleFiles": str,
    "cssClasses": str
}, total=False)

FileInputEventHandlers = TypedDict('FileInputEventHandlers', {
    "ss-file-change": Union[str, Callable]
}, total=False)

FileInputBindings = TypedDict('FileInputBindings', {
    "ss-file-change": str
}, total=False)

WebcamCaptureProps = TypedDict('WebcamCaptureProps', {
    "refreshRate": Union[float, str],
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

WebcamCaptureEventHandlers = TypedDict('WebcamCaptureEventHandlers', {
    "ss-webcam": Union[str, Callable]
}, total=False)

VegaLiteChartProps = TypedDict('VegaLiteChartProps', {
    "spec": Union[Dict, str],
    "cssClasses": str
}, total=False)

VegaLiteChartEventHandlers = TypedDict('VegaLiteChartEventHandlers', {
}, total=False)

PlotlyGraphProps = TypedDict('PlotlyGraphProps', {
    "spec": Union[Dict, str],
    "cssClasses": str
}, total=False)

PlotlyGraphEventHandlers = TypedDict('PlotlyGraphEventHandlers', {
    "plotly-click": Union[str, Callable],
    "plotly-selected": Union[str, Callable],
    "plotly-deselect": Union[str, Callable]
}, total=False)

MetricProps = TypedDict('MetricProps', {
    "name": str,
    "metricValue": str,
    "description": str,
    "note": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "positiveColor": str,
    "neutralColor": str,
    "negativeColor": str,
    "cssClasses": str
}, total=False)

MetricEventHandlers = TypedDict('MetricEventHandlers', {
}, total=False)

MessageProps = TypedDict('MessageProps', {
    "message": str,
    "successColor": str,
    "errorColor": str,
    "warningColor": str,
    "infoColor": str,
    "loadingColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

MessageEventHandlers = TypedDict('MessageEventHandlers', {
}, total=False)

VideoPlayerProps = TypedDict('VideoPlayerProps', {
    "src": str,
    "controls": str,
    "autoplay": str,
    "loop": str,
    "muted": str,
    "cssClasses": str
}, total=False)

VideoPlayerEventHandlers = TypedDict('VideoPlayerEventHandlers', {
}, total=False)

ChatbotProps = TypedDict('ChatbotProps', {
    "incomingInitials": str,
    "outgoingInitials": str,
    "useMarkdown": str,
    "enableFileUpload": str,
    "placeholder": str,
    "incomingColor": str,
    "outgoingColor": str,
    "avatarBackgroundColor": str,
    "avatarTextColor": str,
    "containerBackgroundColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "cssClasses": str
}, total=False)

ChatbotEventHandlers = TypedDict('ChatbotEventHandlers', {
    "ss-chatbot-message": Union[str, Callable],
    "ss-chatbot-action-click": Union[str, Callable],
    "ss-file-change": Union[str, Callable]
}, total=False)

StepProps = TypedDict('StepProps', {
    "name": str,
    "contentPadding": str,
    "isCompleted": str,
    "contentHAlign": str,
    "cssClasses": str
}, total=False)

StepEventHandlers = TypedDict('StepEventHandlers', {
}, total=False)

StepContainerProps = TypedDict('StepContainerProps', {
    "accentColor": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "containerBackgroundColor": str,
    "containerShadow": str,
    "separatorColor": str,
    "buttonColor": str,
    "buttonTextColor": str,
    "buttonShadow": str,
    "cssClasses": str
}, total=False)

StepContainerEventHandlers = TypedDict('StepContainerEventHandlers', {
}, total=False)

RatingInputProps = TypedDict('RatingInputProps', {
    "label": str,
    "feedback": str,
    "minValue": Union[float, str],
    "maxValue": Union[float, str],
    "valueStep": Union[float, str],
    "accentColor": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

RatingInputEventHandlers = TypedDict('RatingInputEventHandlers', {
    "ss-number-change": Union[str, Callable]
}, total=False)

RatingInputBindings = TypedDict('RatingInputBindings', {
    "ss-number-change": str
}, total=False)

TagsProps = TypedDict('TagsProps', {
    "tags": Union[Dict, str],
    "referenceColor": str,
    "seed": Union[float, str],
    "rotateHue": str,
    "primaryTextColor": str,
    "cssClasses": str
}, total=False)

TagsEventHandlers = TypedDict('TagsEventHandlers', {
    "ss-tag-click": Union[str, Callable]
}, total=False)

SwitchInputProps = TypedDict('SwitchInputProps', {
    "label": str,
    "accentColor": str,
    "primaryTextColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

SwitchInputEventHandlers = TypedDict('SwitchInputEventHandlers', {
    "ss-toggle": Union[str, Callable]
}, total=False)

SwitchInputBindings = TypedDict('SwitchInputBindings', {
    "ss-toggle": str
}, total=False)

AvatarProps = TypedDict('AvatarProps', {
    "name": str,
    "imageSrc": str,
    "caption": str,
    "size": str,
    "orientation": str,
    "primaryTextColor": str,
    "secondaryTextColor": str,
    "separatorColor": str,
    "cssClasses": str
}, total=False)

AvatarEventHandlers = TypedDict('AvatarEventHandlers', {
    "ss-click": Union[str, Callable]
}, total=False)

class StreamsyncUIManager(StreamsyncUI):
    """The StreamsyncUIManager class is intended to include dynamically-
    generated methods corresponding to UI components defined in the Vue
    frontend during the build process.

    This class serves as a bridge for programmatically interacting with the
    frontend, allowing methods to adapt to changes in the UI components without
    manual updates.
    """
    
    # Hardcoded classes for proof-of-concept purposes
  
    @staticmethod
    def Root(
            content: RootProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RootEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        The root component of the application, which serves as the starting point of the component hierarchy.
        """
        component = StreamsyncUI.create_container_component(
            'root',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Page(
            content: PageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component representing a single page within the application.
        """
        component = StreamsyncUI.create_container_component(
            'page',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Sidebar(
            content: SidebarProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SidebarEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that organises its children in a sidebar. Its parent must be a Page component.
        """
        component = StreamsyncUI.create_container_component(
            'sidebar',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Button(
            content: ButtonProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ButtonEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A standalone button component that can be linked to a click event handler.
        """
        component = StreamsyncUI.create_component(
            'button',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Text(
            content: TextProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display plain text or formatted text using Markdown syntax.
        """
        component = StreamsyncUI.create_component(
            'text',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Section(
            content: SectionProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SectionEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that divides the layout into sections, with an optional title.
        """
        component = StreamsyncUI.create_container_component(
            'section',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Header(
            content: HeaderProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HeaderEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that typically contains the main navigation elements.
        """
        component = StreamsyncUI.create_container_component(
            'header',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Heading(
            content: HeadingProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HeadingEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A text component used to display headings or titles in different sizes and styles.
        """
        component = StreamsyncUI.create_component(
            'heading',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def DataFrame(
            content: DataFrameProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DataFrameEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display Pandas DataFrames.
        """
        component = StreamsyncUI.create_component(
            'dataframe',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def HTMLElement(
            content: HTMLElementProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HTMLElementEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A generic component that creates customisable HTML elements, which can serve as containers for other components.
        """
        component = StreamsyncUI.create_container_component(
            'html',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Pagination(
            content: PaginationProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PaginationEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that can help you paginate records, for example from a Repeater or a DataFrame.
        """
        component = StreamsyncUI.create_component(
            'pagination',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Repeater(
            content: RepeaterProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RepeaterEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that repeats its child components based on a dictionary.
        """
        component = StreamsyncUI.create_container_component(
            'repeater',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Column(
            content: ColumnProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ColumnEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A layout component that organises its child components in columns. Must be inside a Column Container component.
        """
        component = StreamsyncUI.create_container_component(
            'column',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def ColumnContainer(
            content: ColumnContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ColumnContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        Serves as container for Column components
        """
        component = StreamsyncUI.create_container_component(
            'columns',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Tab(
            content: TabProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TabEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that displays its child components as a tab inside a Tab Container.
        """
        component = StreamsyncUI.create_container_component(
            'tab',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def TabContainer(
            content: TabContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TabContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component for organising and displaying Tab components in a tabbed interface.
        """
        component = StreamsyncUI.create_container_component(
            'tabs',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Link(
            content: LinkProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[LinkEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to create a hyperlink.
        """
        component = StreamsyncUI.create_component(
            'link',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def HorizontalStack(
            content: HorizontalStackProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[HorizontalStackEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.
        """
        component = StreamsyncUI.create_container_component(
            'horizontalstack',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Separator(
            content: SeparatorProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SeparatorEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A visual component to create a separation between adjacent elements.
        """
        component = StreamsyncUI.create_component(
            'separator',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Image(
            content: ImageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ImageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display images.
        """
        component = StreamsyncUI.create_component(
            'image',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def PDF(
            content: PDFProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PDFEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to embed PDF documents.
        """
        component = StreamsyncUI.create_component(
            'pdf',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def IFrame(
            content: IFrameProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[IFrameEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to embed an external resource in an iframe.
        """
        component = StreamsyncUI.create_component(
            'iframe',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def GoogleMaps(
            content: GoogleMapsProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[GoogleMapsEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to embed a Google Map. It can be used to display a map with markers.
        """
        component = StreamsyncUI.create_component(
            'googlemaps',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Mapbox(
            content: MapboxProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MapboxEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to embed a Mapbox map. It can be used to display a map with markers.
        """
        component = StreamsyncUI.create_component(
            'mapbox',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Icon(
            content: IconProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[IconEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display an icon
        """
        component = StreamsyncUI.create_component(
            'icon',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Timer(
            content: TimerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TimerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that emits an event repeatedly at specified time intervals, enabling time-based refresh.
        """
        component = StreamsyncUI.create_component(
            'timer',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def TextInput(
            content: TextInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[TextInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to enter single-line text values.
        """
        component = StreamsyncUI.create_component(
            'textinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def TextareaInput(
            content: TextareaInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TextareaInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[TextareaInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to enter multi-line text values.
        """
        component = StreamsyncUI.create_component(
            'textareainput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def NumberInput(
            content: NumberInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[NumberInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[NumberInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to enter numeric values.
        """
        component = StreamsyncUI.create_component(
            'numberinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def SliderInput(
            content: SliderInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SliderInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[SliderInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to select numeric values using a slider with optional constraints like min, max, and step.
        """
        component = StreamsyncUI.create_component(
            'sliderinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def DateInput(
            content: DateInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DateInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[DateInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to select a date using a date picker interface.
        """
        component = StreamsyncUI.create_component(
            'dateinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def RadioInput(
            content: RadioInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RadioInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[RadioInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to choose a single value from a list of options using radio buttons.
        """
        component = StreamsyncUI.create_component(
            'radioinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def CheckboxInput(
            content: CheckboxInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[CheckboxInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[CheckboxInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to choose multiple values from a list of options using checkboxes.
        """
        component = StreamsyncUI.create_component(
            'checkboxinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def DropdownInput(
            content: DropdownInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[DropdownInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[DropdownInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to select a single value from a list of options using a dropdown menu.
        """
        component = StreamsyncUI.create_component(
            'dropdowninput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def SelectInput(
            content: SelectInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SelectInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[SelectInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to select a single value from a searchable list of options.
        """
        component = StreamsyncUI.create_component(
            'selectinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def MultiselectInput(
            content: MultiselectInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MultiselectInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[MultiselectInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to select multiple values from a searchable list of options.
        """
        component = StreamsyncUI.create_component(
            'multiselectinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def FileInput(
            content: FileInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[FileInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[FileInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to upload files.
        """
        component = StreamsyncUI.create_component(
            'fileinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def WebcamCapture(
            content: WebcamCaptureProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[WebcamCaptureEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A user input component that allows users to capture images using their webcam.
        """
        component = StreamsyncUI.create_component(
            'webcamcapture',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def VegaLiteChart(
            content: VegaLiteChartProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[VegaLiteChartEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that displays Vega-Lite/Altair charts.
        """
        component = StreamsyncUI.create_component(
            'vegalitechart',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def PlotlyGraph(
            content: PlotlyGraphProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[PlotlyGraphEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that displays Plotly graphs.
        """
        component = StreamsyncUI.create_component(
            'plotlygraph',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Metric(
            content: MetricProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MetricEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that prominently displays a metric value and associated information.
        """
        component = StreamsyncUI.create_component(
            'metric',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Message(
            content: MessageProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[MessageEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component that displays a message in various styles, including success, error, warning, and informational.
        """
        component = StreamsyncUI.create_component(
            'message',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def VideoPlayer(
            content: VideoPlayerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[VideoPlayerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A video player component that can play various video formats.
        """
        component = StreamsyncUI.create_component(
            'videoplayer',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Chatbot(
            content: ChatbotProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[ChatbotEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A chatbot component to build human-to-AI interactions.
        """
        component = StreamsyncUI.create_component(
            'chatbot',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def Step(
            content: StepProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[StepEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component that displays its child components as a step inside a Step Container.
        """
        component = StreamsyncUI.create_container_component(
            'step',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def StepContainer(
            content: StepContainerProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[StepContainerEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A container component for displaying Step components, allowing you to implement a stepped workflow.
        """
        component = StreamsyncUI.create_container_component(
            'steps',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def RatingInput(
            content: RatingInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[RatingInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[RatingInputBindings] = None,
            ) -> Component:
        """
        A user input component that allows users to provide a rating.
        """
        component = StreamsyncUI.create_component(
            'ratinginput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def Tags(
            content: TagsProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[TagsEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display coloured tag pills.
        """
        component = StreamsyncUI.create_component(
            'tags',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    
    @staticmethod
    def SwitchInput(
            content: SwitchInputProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[SwitchInputEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None, 
            binding: Optional[SwitchInputBindings] = None,
            ) -> Component:
        """
        A user input component with a simple on/off status.
        """
        component = StreamsyncUI.create_component(
            'switchinput',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible,
            binding=binding)
        return component
    
    @staticmethod
    def Avatar(
            content: AvatarProps = {},
            *,
            id: Optional[str] = None,
            position: Optional[int] = None,
            parentId: Optional[str] = None,
            handlers: Optional[AvatarEventHandlers] = None,
            visible: Optional[Union[bool, str]] = None,
            ) -> Component:
        """
        A component to display user avatars.
        """
        component = StreamsyncUI.create_container_component(
            'avatar',
            content=content,
            id=id,
            position=position,
            parentId=parentId,
            handlers=handlers,
            visible=visible)
        return component
    