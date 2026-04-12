import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { SearchBarComponent } from './search-bar/search-bar.component';
import { AppComponent } from './app.component';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
  declarations: [SearchBarComponent, AppComponent],
  imports: [
    BrowserModule,
    RouterOutlet,
    HttpClientModule,
    CommonModule,
    FormsModule,
    MarkdownModule.forRoot(),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
