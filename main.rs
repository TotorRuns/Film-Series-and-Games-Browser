extern crate reqwest;
extern crate serde_json;
extern crate gtk;
extern crate dotenv;

use std::io::{self, Write};
use serde_json::Value;
use gtk::prelude::*;
use gtk::{Window, WindowType, Label, Box, Orientation, Image};
use dotenv::dotenv;
use std::env;

fn main() {
    dotenv().ok();
    gtk::init().expect("Failed to initialize GTK.");

    let window = Window::new(WindowType::Toplevel);
    window.set_title("Film-Informationen");
    window.set_default_size(800, 600);

    let vbox = Box::new(Orientation::Vertical, 10);
    window.add(&vbox);

    let label = Label::new(Some("Bitte geben Sie den Namen des Films ein:"));
    vbox.pack_start(&label, false, false, 0);

    let entry = gtk::Entry::new();
    vbox.pack_start(&entry, false, false, 0);

    let button = gtk::Button::with_label("Suchen");
    vbox.pack_start(&button, false, false, 0);

    let result_box = Box::new(Orientation::Vertical, 10);
    vbox.pack_start(&result_box, true, true, 0);

    button.connect_clicked(clone!(@strong entry, @strong result_box => move |_| {
        let movie_name = entry.get_text().to_string();
        let movie_info = fetch_movie_info(&movie_name);
        result_box.foreach(|child| result_box.remove(child));
        if let Some(info) = movie_info {
            let poster_url = fetch_movie_poster(&info["imdbID"].as_str().unwrap());
            display_movie_info(&result_box, &info, &poster_url);
        } else {
            let error_label = Label::new(Some("Film nicht gefunden!"));
            result_box.pack_start(&error_label, false, false, 0);
        }
        result_box.show_all();
    }));

    window.connect_delete_event(|_, _| {
        gtk::main_quit();
        Inhibit(false)
    });

    window.show_all();
    gtk::main();
}

fn fetch_movie_info(movie_name: &str) -> Option<Value> {
    let api_key = env::var("OMDB_API_KEY").expect("OMDB_API_KEY nicht gesetzt");
    let url = format!("http://www.omdbapi.com/?t={}&apikey={}", movie_name, api_key);

    let response: Value = reqwest::blocking::get(&url)
        .expect("Fehler beim Senden der Anfrage")
        .json()
        .expect("Fehler beim Parsen der Antwort");

    if response["Response"] == "True" {
        Some(response)
    } else {
        None
    }
}

fn fetch_movie_poster(imdb_id: &str) -> String {
    let api_key = env::var("TMDB_API_KEY").expect("TMDB_API_KEY nicht gesetzt");
    let url = format!("https://api.themoviedb.org/3/movie/{}?api_key={}", imdb_id, api_key);

    let response: Value = reqwest::blocking::get(&url)
        .expect("Fehler beim Senden der Anfrage")
        .json()
        .expect("Fehler beim Parsen der Antwort");

    format!("https://image.tmdb.org/t/p/w500{}", response["poster_path"].as_str().unwrap())
}

fn fetch_game_info(game_name: &str) -> Option<Value> {
    let api_key = env::var("RAWG_API_KEY").expect("RAWG_API_KEY nicht gesetzt");
    let url = format!("https://api.rawg.io/api/games?key={}&search={}", api_key, game_name);

    let response: Value = reqwest::blocking::get(&url)
        .expect("Fehler beim Senden der Anfrage")
        .json()
        .expect("Fehler beim Parsen der Antwort");

    if response["count"].as_i64().unwrap() > 0 {
        Some(response["results"][0].clone())
    } else {
        None
    }
}

fn display_movie_info(result_box: &Box, info: &Value, poster_url: &str) {
    let title_label = Label::new(Some(&format!("Titel: {}", info["Title"])));
    result_box.pack_start(&title_label, false, false, 0);

    let year_label = Label::new(Some(&format!("Jahr: {}", info["Year"])));
    result_box.pack_start(&year_label, false, false, 0);

    let genre_label = Label::new(Some(&format!("Genre: {}", info["Genre"])));
    result_box.pack_start(&genre_label, false, false, 0);

    let director_label = Label::new(Some(&format!("Regisseur: {}", info["Director"])));
    result_box.pack_start(&director_label, false, false, 0);

    let actors_label = Label::new(Some(&format!("Schauspieler: {}", info["Actors"])));
    result_box.pack_start(&actors_label, false, false, 0);

    let plot_label = Label::new(Some(&format!("Plot: {}", info["Plot"])));
    result_box.pack_start(&plot_label, false, false, 0);

    let poster_image = Image::new_from_url(poster_url);
    result_box.pack_start(&poster_image, false, false, 0);
}

