-- Press a button to send a GET request for random cat GIFs.
--
-- Read how it works:
--   https://guide.elm-lang.org/effects/json.html
--


module Main exposing (..)

import Browser
import File.Download as Download
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Url.Builder exposing (..)



-- MAIN


main : Program String Model Msg
main =
    Browser.document
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }



-- MODEL


type alias Model =
    { content : String
    , profile : String
    , status : LoadingStatus
    }


type LoadingStatus
    = Failure
    | Loading
    | Success String


init : String -> ( Model, Cmd Msg )
init profile =
    ( Model "" profile (Success "https://media.giphy.com/media/13Zdt5rMO2Ngc0/giphy.gif")
    , Cmd.none
    )



-- UPDATE


type Msg
    = RegisterURL
    | RecvHash (Result Http.Error String)
    | EditURL String
    | DownloadNewKey
    | PostProfile
    | ProfileUpdated (Result Http.Error String)
    | EditProfile String


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        RegisterURL ->
            ( { model | status = Loading }, getHash model.content )

        RecvHash result ->
            case result of
                Ok hash ->
                    ( { model | status = Success hash }, Cmd.none )

                Err _ ->
                    ( { model | status = Failure }, Cmd.none )

        EditURL content ->
            ( { model | content = content }, Cmd.none )

        DownloadNewKey ->
            ( model, getNewKey )

        PostProfile ->
            ( model, updateProfile model.profile )

        ProfileUpdated result ->
            case result of
                Ok _ ->
                    -- We don't need to do anything, profile model is set.
                    ( model, Cmd.none )

                Err _ ->
                    -- TODO Should define additional error state?
                    ( { model | status = Failure }, Cmd.none )

        EditProfile profile ->
            ( { model | profile = profile }, Cmd.none )



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- VIEW


view : Model -> Browser.Document Msg
view model =
    { title = "FlowKarma.Live"
    , body =
        [ pure_full_width
            [ h1 [] [ text "FlowKarma.Live" ] ]
        , labeled_div "About You"
            [ Html.form [ class "pure-form", onSubmit PostProfile ]
                [ textarea [ class "pure-input-1", onInput EditProfile ]
                    [ text model.profile ]
                , button [ class "pure-button" ]
                    [ text "Update" ]
                ]
            ]
        , labeled_div "Share an URL"
            [ Html.form [ class "pure-form", onSubmit RegisterURL ]
                [ input
                    [ placeholder "URL to share."
                    , class "pure-input-1"
                    , value model.content
                    , onInput EditURL
                    ]
                    []
                ]
            , viewGif model
            ]
        , labeled_div "Invite New Members"
            [ button [ onClick DownloadNewKey, class "pure-button" ]
                [ text "Download key cert file to let a friend join." ]
            ]
        ]
    }


pure_full_width : List (Html msg) -> Html msg
pure_full_width children =
    div [ class "pure-g" ]
        [ div [ class "pure-u-1-1" ]
            [ div [ class "l-box" ] children ]
        ]


labeled_div : String -> List (Html msg) -> Html msg
labeled_div label children =
    pure_full_width [ fieldset [] (legend [] [ text label ] :: children) ]


viewGif : Model -> Html Msg
viewGif model =
    let
        button_attrs =
            [ onClick RegisterURL, class "pure-button" ]

        bb label =
            button button_attrs [ text label ]
    in
    case model.status of
        Failure ->
            div []
                [ text "I could not load a random cat for some reason. "
                , bb "Try Again!"
                ]

        Loading ->
            text "Loading..."

        Success url ->
            div []
                [ bb "Get Share URL"
                , pre [] [ a [ href url ] [ text url ] ]
                ]



-- HTTP


getHash : String -> Cmd Msg
getHash url =
    Http.post
        { body = Http.emptyBody
        , url = absolute [ "reg" ] [ string "url" url ]
        , expect = Http.expectString RecvHash
        }


getNewKey : Cmd Msg
getNewKey =
    Download.url "newkey"


updateProfile : String -> Cmd Msg
updateProfile profile =
    Http.post
        { body = Http.stringBody "text/plain" profile
        , url = absolute [ "profile" ] []
        , expect = Http.expectString ProfileUpdated
        }
