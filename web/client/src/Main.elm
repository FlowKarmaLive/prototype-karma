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
    , share_status : LoadingStatus
    , profile_status : LoadingStatus
    }


type LoadingStatus
    = Failure
    | Loading
    | Success String


init : String -> ( Model, Cmd Msg )
init profile =
    ( Model
        ""
        profile
        (Success "https://media.giphy.com/media/13Zdt5rMO2Ngc0/giphy.gif")
        (Success "")
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
            ( { model | share_status = Loading }, getHash model.content )

        RecvHash result ->
            case result of
                Ok hash ->
                    ( { model | share_status = Success hash }, Cmd.none )

                Err _ ->
                    ( { model | share_status = Failure }, Cmd.none )

        EditURL content ->
            ( { model | content = content }, Cmd.none )

        DownloadNewKey ->
            ( model, getNewKey )

        PostProfile ->
            ( { model | profile_status = Loading }, updateProfile model.profile )

        ProfileUpdated result ->
            case result of
                Ok _ ->
                    -- We don't need to do anything, profile model is set.
                    ( { model | profile_status = Success "" }, Cmd.none )

                Err _ ->
                    -- TODO Should define additional error state?
                    ( { model | profile_status = Failure }, Cmd.none )

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
                , button
                    [ class "pure-button"
                    , disabled (model.profile_status == Loading)
                    ]
                    [ text "Update" ]
                , viewProfileStatus model.profile_status
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
                , button
                    [ class "pure-button"
                    , disabled (model.share_status == Loading)
                    ]
                    [ text "Share URL (ShURL)" ]
                ]
            , viewShareStatus model.share_status
            ]
        , labeled_div "Invite New Members"
            [ bb DownloadNewKey "Download key cert file to let a friend join." ]
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
    let
        kids =
            legend [] [ text label ] :: children
    in
    pure_full_width [ fieldset [] kids ]


bb : Msg -> String -> Html Msg
bb event label =
    button [ onClick event, class "pure-button" ] [ text label ]



-- If a button is in a form, clicking it triggers onSubmit, and if the
-- button also has onClick, the submission happens twice!


viewShareStatus : LoadingStatus -> Html Msg
viewShareStatus share_status =
    let
        t =
            case share_status of
                Failure ->
                    text "I could not load a random cat for some reason."

                Loading ->
                    text "Loading..."

                Success url ->
                    a [ href url ] [ text url ]
    in
    div [] [ pre [] [ t ] ]


viewProfileStatus : LoadingStatus -> Html Msg
viewProfileStatus profile_status =
    case profile_status of
        Failure ->
            text ""

        Loading ->
            text "Updating..."

        Success url ->
            text ""



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
