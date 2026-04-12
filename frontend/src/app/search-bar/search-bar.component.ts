import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss'],
})
export class SearchBarComponent {
    @Output() searchValue = new EventEmitter<string>();
    @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

    onSearch(value: string): void {
        // if (!this.validatePostcode(value)) {
        // alert('Please enter a valid UK postcode.');
        // return;
        // }
        this.searchValue.emit(value);
        console.log('Search initiated for postcode:', value);
    }

    validatePostcode(postcode: string): boolean {
        const postcodeRegex = /^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$/i;
        return postcodeRegex.test(postcode.trim());
    }

    focusInput(): void {
        this.searchInput.nativeElement.focus();
    }

}
